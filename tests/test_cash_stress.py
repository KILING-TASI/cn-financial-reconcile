import copy, json, unittest
from pathlib import Path
from cnreconcile.cash_stress import calculate


class Tests(unittest.TestCase):
    def sample(self):
        base=json.loads((Path(__file__).parents[1]/'examples/dividend-teaching-v2.json').read_text('utf-8'))
        return dict(inputSchema='cash-demand-stress/1',baseline=base,scenarios=[dict(id='base',note='明确假设无新增需求',operatingCashChange='0',capexChange='0',additionalDemand='0')])
    def test_cash_bridge_uses_basic_currency(self):
        spec=self.sample(); row=calculate(spec)['scenarios'][0]
        self.assertEqual(row['marginAfterAdditionalDemand'],'300000'); self.assertEqual(row['status'],'covered-under-assumptions')
    def test_unknown_demand_not_zero(self):
        spec=self.sample(); spec['scenarios'][0]['additionalDemand']=None
        row=calculate(spec)['scenarios'][0]; self.assertIsNone(row['marginAfterAdditionalDemand']); self.assertEqual(row['status'],'unknown')
    def test_stress_shortfall_and_signed_margin(self):
        spec=self.sample(); spec['scenarios'][0].update(operatingCashChange='-0.5',capexChange='0.5',additionalDemand='10000')
        row=calculate(spec)['scenarios'][0]; self.assertEqual(row['marginAfterAdditionalDemand'],'-510000.0'); self.assertEqual(row['incrementalDemandCapacity'],'0')
    def test_period_mismatch_retains_unknown(self):
        spec=self.sample(); spec['baseline']['facts']['declaredDividend']['attributablePeriod']='2024-12-31'
        self.assertEqual(calculate(spec)['scenarios'][0]['status'],'unknown')
    def test_negative_demand_duplicate_id_nonfinite_rejected(self):
        for field,value in [('additionalDemand','-1'),('operatingCashChange','NaN'),('capexChange','-2')]:
            spec=self.sample(); spec['scenarios'][0][field]=value
            with self.assertRaises(ValueError): calculate(spec)
        spec=self.sample(); spec['scenarios']*=2
        with self.assertRaises(ValueError): calculate(spec)


if __name__=='__main__': unittest.main()
