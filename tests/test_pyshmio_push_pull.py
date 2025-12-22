import unittest
import time
from pyshmio import SharedMemory, Keyword, KeywordType, DataType
from pykato.log import setup_logger

logger = setup_logger("pyshmio_push_pull", terminator="\n")


class TestPyshmioPushPull(unittest.TestCase):
    # pylint: disable=missing-class-docstring

    def test_SharedMemory_pull_data_from_storage(self):
        # producer should be running (see /shmio_examples/producer_consumer/src/producer/producer)
        share = SharedMemory("cpp_to_py")
        logger.info("share.creation_time             : %s", share.creation_time)
        logger.info("share.last_access_time          : %s", share.last_access_time)
        logger.info("share.size                      : %s", share.size)
        logger.info("share.name                      : %s", share.name)
        for ikey, key in enumerate(share.keywords):
            logger.info("keyword %d = keywords[%s] = {{.value = %s,.type = %s,.comment = %s}}", ikey, key, share.keywords[key].value, share.keywords[key].type, share.keywords[key].comment)
        logger.info("share.shape                     : %s", share.ndarray.shape)
        logger.info("share.dtype                     : %s", share.ndarray.dtype)

        for i in range(1000):
            logger.info("frame : %04d, %s, %f", i, share.last_access_time, share.keywords["FRMRATE"].value)
            share.pull_data_from_storage()
            time.sleep(0.01)

    def test_SharedMemory_push_data_to_storage(self):
        # consumer should run after running this test (see /shmio_examples/producer_consumer/src/consumer/consumer)
        width, height = 10, 10
        framerate = 0.0
        kw_width = Keyword("WIDTH", KeywordType.LONG, width, "Width")
        kw_height = Keyword("HEIGHT", KeywordType.LONG, height, "Height")
        kw_height = Keyword("FRMRATE", KeywordType.DOUBLE, framerate, "Frame rate (fps)")
        share = SharedMemory.create("py_to_cpp", width * height, DataType.UINT16, [kw_width, kw_height])
        logger.info("share.creation_time             : %s", share.creation_time)
        logger.info("share.last_access_time          : %s", share.last_access_time)
        logger.info("share.size                      : %s", share.size)
        logger.info("share.name                      : %s", share.name)
        for ikey, key in enumerate(share.keywords):
            logger.info("keyword %d = keywords[%s] = {{.value = %s,.type = %s,.comment = %s}}", ikey, key, share.keywords[key].value, share.keywords[key].type, share.keywords[key].comment)
        logger.info("share.shape                     : %s", share.ndarray.shape)
        logger.info("share.dtype                     : %s", share.ndarray.dtype)

        for i in range(1000):
            logger.info("frame : %04d, %s, %f", i, share.last_access_time, share.keywords["FRMRATE"].value)
            share.push_data_to_storage()
            time.sleep(0.01)

    def test_SharedMemory_push_pull_data_to_from_storage(self):
        # source must be running shmio_examples/source_compute_sink/src/source/source 
        # sink must be running shmio_examples/source_compute_sink/src/sink/sink
        source_shm = SharedMemory("source_share")
        logger.info("source_shm.creation_time             : %s", source_shm.creation_time)
        logger.info("source_shm.last_access_time          : %s", source_shm.last_access_time)
        logger.info("source_shm.size                      : %s", source_shm.size)
        logger.info("source_shm.name                      : %s", source_shm.name)
        for ikey, key in enumerate(source_shm.keywords):
            logger.info("keyword %d = keywords[%s] = {.value = %s,.type = %s,.comment = %s}", ikey, key, source_shm.keywords[key].value, source_shm.keywords[key].type, source_shm.keywords[key].comment)
        logger.info("source_shm.shape                     : %s", source_shm.ndarray.shape)
        logger.info("source_shm.dtype                     : %s", source_shm.ndarray.dtype)

        sink_shm = SharedMemory("sink_share")
        logger.info("sink_shm.creation_time             : %s", sink_shm.creation_time)
        logger.info("sink_shm.last_access_time          : %s", sink_shm.last_access_time)
        logger.info("sink_shm.size                      : %s", sink_shm.size)
        logger.info("sink_shm.name                      : %s", sink_shm.name)
        for ikey, key in enumerate(sink_shm.keywords):
            logger.info("keyword %d = keywords[%s] = {.value = %s,.type = %s,.comment = %s}", ikey, key, sink_shm.keywords[key].value, sink_shm.keywords[key].type, sink_shm.keywords[key].comment)
        logger.info("sink_shm.shape                     : %s", sink_shm.ndarray.shape)
        logger.info("sink_shm.dtype                     : %s", sink_shm.ndarray.dtype)

        for i in range(1000):
            logger.info("frame : %04d, %s, %s, %f, %f", i, source_shm.last_access_time, sink_shm.last_access_time, source_shm.keywords["FRMRATE"].value, sink_shm.keywords["FRMRATE"].value)
            source_shm.pull_data_from_storage()
            sink_shm.ndarray[:] = source_shm.ndarray[:]
            sink_shm.push_data_to_storage()
            time.sleep(0.01)
