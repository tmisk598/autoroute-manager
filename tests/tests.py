import os
import sys
import unittest

import numpy as np
import pandas as pd
from osgeo import gdal

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from autoroute.autoroute import AutoRouteHandler

@unittest.skip
class TestStreamRasterization(unittest.TestCase):
    def setUp(self) -> None:
        self.params = {"OVERWRITE": True,
              "DATA_DIR": "test_ar_data",
              "DEM_FOLDER": "tests/test_data/DEMs/single_4326",
              "BUFFER_FILES": False, 
              "DEM_NAME": "test_dem", 
              "STREAM_NETWORK_FOLDER": "tests/test_data/streamlines/single_4326", 
              "STREAM_NAME": "test_strm", 
              "STREAM_ID": "LINKNO" }
        self.output = "test_ar_data/stream_files/test_dem__test_strm/N18W073_FABDEM_V1-2__strm.tif"
        self.validation = "tests/test_data/validation/rasterization/N18W073_FABDEM_V1-2__strm_val.tif"
        
    def tearDown(self) -> None:
        if self.output and os.path.exists(self.output): os.remove(self.output) 
        
    def test_sameProjection_gpkg_singleFiles(self):
        AutoRouteHandler(self.params).run()

        self.assertTrue(os.path.exists(self.output))
        out_ds = gdal.Open(self.output)
        self.assertIsNotNone(out_ds)
        val_ds = gdal.Open(self.validation)
        self.assertTrue(np.count_nonzero(~(out_ds.ReadAsArray() == val_ds.ReadAsArray())) <= 26, "Arrays are not equal") # Slightly different geometry, but we should get the same answer. Parquet tends to be more "correct" than gpkg
        self.assertEqual(out_ds.GetGeoTransform(), val_ds.GetGeoTransform(), "GeoTransform is not equal")
        self.assertEqual(out_ds.GetProjection(), val_ds.GetProjection(), "Projection is not equal")

    def test_sameProjection_parquet_singleFiles(self):
        self.params["STREAM_NETWORK_FOLDER"] = "tests/test_data/streamlines/single_parquet_4326"
        AutoRouteHandler(self.params).run()

        self.assertTrue(os.path.exists(self.output))
        out_ds = gdal.Open(self.output)
        self.assertIsNotNone(out_ds)
        val_ds = gdal.Open(self.validation)
        self.assertTrue(np.array_equal(out_ds.ReadAsArray(), val_ds.ReadAsArray()), "Arrays are not equal")
        self.assertEqual(out_ds.GetGeoTransform(), val_ds.GetGeoTransform(), "GeoTransform is not equal")
        self.assertEqual(out_ds.GetProjection(), val_ds.GetProjection(), "Projection is not equal")

    def test_difProjection_parquet_singleFiles(self):
        self.params["STREAM_NETWORK_FOLDER"] = "tests/test_data/streamlines/single_parquet_3857"
        AutoRouteHandler(self.params).run()

        self.assertTrue(os.path.exists(self.output))
        out_ds = gdal.Open(self.output)
        self.assertIsNotNone(out_ds)
        val_ds = gdal.Open(self.validation)
        self.assertTrue(np.array_equal(out_ds.ReadAsArray(), val_ds.ReadAsArray()), "Arrays are not equal")
        self.assertEqual(out_ds.GetGeoTransform(), val_ds.GetGeoTransform(), "GeoTransform is not equal")
        self.assertEqual(out_ds.GetProjection(), val_ds.GetProjection(), "Projection is not equal")

    def test_various_files_and_projections(self):
        self.params["STREAM_NETWORK_FOLDER"] = "tests/test_data/streamlines/multiple_parquet_various"

        AutoRouteHandler(self.params).run()

        self.assertTrue(os.path.exists(self.output))
        out_ds = gdal.Open(self.output)
        self.assertIsNotNone(out_ds)
        val_ds = gdal.Open(self.validation)
        self.assertTrue(np.count_nonzero(~(out_ds.ReadAsArray() == val_ds.ReadAsArray())) <= 17, "Arrays are not equal") # Slightly different, due to gpkg again
        self.assertEqual(out_ds.GetGeoTransform(), val_ds.GetGeoTransform(), "GeoTransform is not equal")
        self.assertEqual(out_ds.GetProjection(), val_ds.GetProjection(), "Projection is not equal")

@unittest.skip
class TestRowColIdFIle(unittest.TestCase):
    def setUp(self) -> None:
        self.params = {"OVERWRITE": True,
              "DATA_DIR": "test_ar_data",
              "DEM_FOLDER": "",
              "BUFFER_FILES": False, 
              "DEM_NAME": "test_dem", 
              "STREAM_NETWORK_FOLDER": "/Users/ricky/Desktop/MAC/MAC/StreamlineShapefile", 
              "STREAM_NAME": "test_strm", 
              "STREAM_ID": "COMID",
               "FLOWFILE":  "/Users/ricky/Desktop/MAC/MAC/FlowFile/DR_test.txt",
               "ID_COLUMN": "COMID",
               "FLOW_COLUMN": "DR_Histori",
               "BASE_FLOW_COLUMN": "base"}
        self.output = "test_ar_data/rapid_files/test_dem__test_strm/DR_DEM_FULL__strm__row_col_id.txt"
        self.validation = "tests/test_data/validation/row_id_flow/Dr_test.txt"

    def tearDown(self) -> None:
        if self.output and os.path.exists(self.output): os.remove(self.output) 

    def test_row_col_id_file(self):
        AutoRouteHandler(self.params).run()

        self.assertTrue(os.path.exists(self.output))
        out_df = pd.read_csv(self.output)
        val_df = pd.read_csv(self.validation)
        self.assertTrue(out_df.equals(val_df), "Dataframes are not equal")

    def test_row_col_id_file_no_inputs(self):
        self.params["ID_COLUMN"] = ""
        self.params["FLOW_COLUMN"] = ""
        self.params["BASE_FLOW_COLUMN"] = ""
        AutoRouteHandler(self.params).run()

        self.assertTrue(os.path.exists(self.output))
        out_df = pd.read_csv(self.output)
        val_df = pd.read_csv(self.validation)
        self.assertTrue(out_df.equals(val_df), "Dataframes are not equal")

class TestLandUse(unittest.TestCase):
    def setUp(self) -> None:
        self.params = {"OVERWRITE": True,
              "DATA_DIR": "/Users/ricky/autoroute-manager/test_ar_data",
              "DEM_FOLDER": "tests/test_data/DEMs/single_4326",
              "BUFFER_FILES": False, 
              "DEM_NAME": "test_dem", }
        self.output = "test_ar_data/land_use/test_dem/N18W073_FABDEM_V1-2__lu.vrt"
        self.validation = "tests/test_data/validation/LU/same_proj/lu.tif"
        
    def tearDown(self) -> None:
        pass
        if self.output and os.path.exists(self.output): os.remove(self.output) 
        
    def test_land_use_samesize(self):
        self.params['LAND_USE_FOLDER'] = "tests/test_data/LUs/single_4326"
        AutoRouteHandler(self.params).run()

        if not os.path.exists(self.output):
            self.output = self.output.replace(".vrt", ".tif")
        self.assertTrue(os.path.exists(self.output))
        out_ds = gdal.Open(self.output)
        self.assertIsNotNone(out_ds)
        val_ds = gdal.Open(self.validation)
        self.assertTrue(np.array_equal(out_ds.ReadAsArray(), val_ds.ReadAsArray()), "Arrays are not equal")
        self.assertEqual(out_ds.GetGeoTransform(), val_ds.GetGeoTransform(), "GeoTransform is not equal")
        self.assertEqual(out_ds.GetProjection(), val_ds.GetProjection(), "Projection is not equal")

    def test_land_use_multiple_projected(self):
        self.params['LAND_USE_FOLDER'] = "tests/test_data/LUs/multiple_nad"
        self.validation = "tests/test_data/validation/LU/dif_proj/lu.tif" # Projection slightly rotates output, which is close enough
        AutoRouteHandler(self.params).run()

        if not os.path.exists(self.output):
            self.output = self.output.replace(".vrt", ".tif")
        self.assertTrue(os.path.exists(self.output))
        out_ds = gdal.Open(self.output)
        self.assertIsNotNone(out_ds)
        val_ds = gdal.Open(self.validation)
        self.assertTrue(np.array_equal(out_ds.ReadAsArray(), val_ds.ReadAsArray()), "Arrays are not equal")
        self.assertEqual(out_ds.GetGeoTransform(), val_ds.GetGeoTransform(), "GeoTransform is not equal")
        self.assertEqual(out_ds.GetProjection(), val_ds.GetProjection(), "Projection is not equal")


if __name__ == '__main__':
    unittest.main()