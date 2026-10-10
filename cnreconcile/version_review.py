"""Selected original/revised text occurrences, never a full-statement audit."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from .engine import verify_pdf_quote
from .cli_feedback import utf8_console, failure, saved
from .table_extract import validate_versions


def calculate(spec):
    import copy
    spec = copy.deepcopy(spec)
    if spec.get('inputSchema') != 'version-selected-fields-v1' or spec.get('methodVersion') != 'bound-selected-occurrences-1':
        raise ValueError('未知选定版本核验schema或方法')
    lineage = validate_versions(spec['documents'], spec['relations'], spec['asOf'])
    docs = {row['id']: row for row in spec['documents']}
    pairs, seen = [], set()
    if not isinstance(spec['fieldPairs'], list) or not 1 <= len(spec['fieldPairs']) <= 100:
        raise ValueError('须给出1至100个选定出现位置')
    for pair in spec['fieldPairs']:
        if not isinstance(pair.get('id'), str) or not pair['id'] or pair['id'] in seen:
            raise ValueError('选定出现位置标识须唯一')
        seen.add(pair['id']);states = {}
        for side in ('before', 'after'):
            item = pair[side];doc = docs.get(item['documentId'])
            if not doc or not isinstance(item.get('value'), str) or not item['value']:
                raise ValueError('选定值或原文身份缺失')
            if item['value'] not in item['quote']:
                raise ValueError('选定值未绑定原文短引句')
            if doc.get('pdfPath'):
                path = Path(doc['pdfPath'])
                if not path.is_file() or path.stat().st_size > 64 * 1024 * 1024 or hashlib.sha256(path.read_bytes()).hexdigest() != doc['sha256']:
                    raise ValueError('选定版本文件SHA不一致')
            states[side] = verify_pdf_quote(dict(page=item['page'], quote=item['quote'], pdfPath=doc.get('pdfPath')))
            if doc.get('pdfPath') and states[side] != 'quote-found-on-page':
                raise ValueError('选定值短引句未在原页找到')
        b, a = docs[pair['before']['documentId']], docs[pair['after']['documentId']]
        if b['entity'] != a['entity'] or b['publishedAt'] > a['publishedAt']:
            raise ValueError('选定对照主体或版本顺序不同')
        edges = [edge for edge in spec['relations'] if edge['from'] == b['id'] and edge['to'] == a['id']]
        if not edges or (pair['before']['value'] != pair['after']['value'] and not any(pair['id'] in edge['fields'] for edge in edges)):
            raise ValueError('选定变化未绑定受影响字段及版本关系')
        pairs.append(dict(id=pair['id'], before=pair['before'], after=pair['after'], evidenceStatus=states,
                          status='changed' if pair['before']['value'] != pair['after']['value'] else 'unchanged'))
    # Never publish local source paths in the portable evidence record.
    for doc in lineage['documents']:
        doc.pop('pdfPath', None)
    for edge in lineage['relations']:
        edge['evidence'].pop('pdfPath', None)
    return dict(inputSchema='version-selected-fields-v1', methodVersion='bound-selected-occurrences-1', asOf=spec['asOf'],
                lineage=lineage, fieldPairs=pairs, latestVersionStatus='not-certified',
                limitations=['仅输入选定出现位置；同名字段其他出现位置/全部金额未核', '更正公告仅作为关联依据，原始/修订文件分别核验，不能拿公告代替双版',
                             '不自动选最新版，不恢复历史事前可得，不出审计意见；未核页保持声明状态'])


def publish(spec, out):
    import copy
    result = calculate(copy.deepcopy(spec));out = Path(out)
    if out.exists():raise ValueError('另存新目录，不覆盖旧核验')
    body = '# 选定版本原文对照\n\n仅核本次选定位置，不能解释成整份报表已验收或当前最新版已认证。\n\n'
    for pair in result['fieldPairs']:
        body += pair['id'] + '：原始值' + pair['before']['value'] + '，修订值' + pair['after']['value'] + '；' + ('本处发生变化' if pair['status']=='changed' else '本处未变') + '。\n\n'
        for side in ('before','after'):
            item=pair[side];body += ('原始版' if side=='before' else '修订版') + '物理页' + str(item['page']) + '：' + item['quote'] + '；' + ('绑定页短引句已找到' if pair['evidenceStatus'][side]=='quote-found-on-page' else '本次未核页') + '。\n\n'
    for doc in result['lineage']['documents']:
        body += '版本' + doc['version'] + '，公布' + doc['publishedAt'] + '；来源' + str(doc.get('source') or '未知') + '，SHA256 ' + doc['sha256'] + '。\n\n'
    body += '\n\n'.join(result['limitations'])
    out.mkdir(parents=True)
    for name,text in [('input.json',json.dumps(spec,ensure_ascii=False,indent=2)),('result.json',json.dumps(result,ensure_ascii=False,indent=2)),('版本对照.md',body),('版本对照.html','<!doctype html><meta charset="utf-8"><title>版本对照</title><main style="max-width:900px;margin:40px auto;font:18px/1.8 sans-serif;white-space:pre-wrap">'+html.escape(body)+'</main>')]:
        (out/name).write_text(text,encoding='utf-8')
    return result


if __name__=='__main__':
    utf8_console()
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--out-dir',required=True);args=p.parse_args()
    try:
        publish(json.loads(args.input.read_text('utf-8-sig')),args.out_dir)
        saved('选定版本核验报告',args.out_dir,Path(args.out_dir)/'版本对照.html')
    except (ValueError,OSError,KeyError,TypeError,ImportError) as error:p.exit(2,failure(error,args.out_dir))
