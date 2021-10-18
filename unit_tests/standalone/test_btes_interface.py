import os
import tempfile
import unittest

from glhe.utilities.functions import load_json
from glhe.utilities.functions import write_json
from standalone.btes_interface import BTES_interface

norm = os.path.normpath
join = os.path.join


class TestBtesInterface(unittest.TestCase):

    def setUp(self):
        self.this_file_directory = os.path.dirname(os.path.realpath(__file__))

    def test_operate(self):
        temp_dir = tempfile.mkdtemp()
        temp_file = join(temp_dir, 'in.json')
        test_dir = norm(join(self.this_file_directory, '..', '..', 'test_files'))
        btes = BTES_interface("test_file.json", test_dir)
        # test von operate_btes:
        ser = []
        # time_index = 
        years_to_sim = 1
        i_list = [0,1,10,50,100,500,1000,1500,2000]
        for i in range(24 * 365 * years_to_sim):
            # i = i+1
            if i in i_list:
                params = btes.operate_btes((i)*3600, 3600, 0.446, 10)
                print(params.temperature)
                ser.append(params.temperature)
            else:
                temp = btes.ghe.lts_ghe.bh_wall_temperature
                params = btes.operate_btes((i)*3600, 3600, 0.446, temp)
                print(params.temperature)
                ser.append(params.temperature)
        self.assertAlmostEqual(ser[1], 8.887, delta=0.01)

    def test_simulate(self):
        # test does not work yet...
        # %% test von simulation run - grundsätzliche Funktion.
        # now = str(datetime.now())[0:16]
        # years_to_sim = 1
        # btes.run_sim(years_to_sim,
        #               json_path=join(cwd, test_dir, "test_file.json"),
        #               loaddata_path=join(cwd, test_dir, "HP_Loads_ODT.csv"),
        #               add_id=now)
        # df_self = pd.read_csv(
        #     join(test_dir, 'out_{}-yr_self{}.csv'.format(years_to_sim, now)),
        #     index_col=0, parse_dates=True)
        # test Ergebnisse der Simu plotten
        # fig = plt.figure()
    
        # ax = fig.add_subplot(111)
    
        # cols = [
        #     # 'GroundHeatExchangerLTS:SELF-GHE:BH Resist. [m-K/W]',
        #     # 'GroundHeatExchangerLTS:SELF-GHE:Heat Rate [W]',
        #     'GroundHeatExchangerLTS:SELF-GHE:Inlet Temp. [C]',
        #     'GroundHeatExchangerLTS:SELF-GHE:Outlet Temp. [C]',
        #     # 'SwedishHP:SVENSKA VARMMEPUMPE:COP [-]',
        #     'SwedishHP:SVENSKA VARMMEPUMPE:Outdoor Air Temp. [C]',
        #     # 'SwedishHP:SVENSKA VARMMEPUMPE:Load-side Heat Rate [W]',
        #     # 'PlantLoop:Demand Inlet Temp. [C]',
        #     # 'PlantLoop:Demand Outlet Temp. [C]',
        #     # 'PlantLoop:Supply Inlet Temp. [C]',
        #     # 'PlantLoop:Supply Outlet Temp. [C]',
        #     # 'ConstantFlow:CONSTANT FLOW:Flow Rate [kg/s]',
        #     # 'SwedishHP:SVENSKA VARMMEPUMPE:Outlet Temp. [C]',
        #     # 'SwedishHP:SVENSKA VARMMEPUMPE:Inlet Temp. [C]',
        #     # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:Heat Rate [W]',
        #     # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:BH Heat Rate [W]',
        #     # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:Inlet Temp. [C]',
        #     # 'SingleUTubeBHGrouted:AVERAGE-BOREHOLE:Outlet Temp. [C]',
        #     # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Inlet Temp. Leg 1 [C]',
        #     # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Inlet Temp. Leg 2 [C]',
        #     # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Outlet Temp. Leg 1 [C]',
        #     # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:1:Outlet Temp. Leg 2 [C]',
        #     # 'SegmentUTubeBHGrouted:BH:average-borehole:Seg:2:Outlet Temp. [C]',
        # ]
    
        # for col in cols:
        #     ax.plot(df_self[col], label=col)
        #     # ax.plot(df_cross[col], label=col+"cross")
    
        # plt.legend()
        # plt.show()
        pass
