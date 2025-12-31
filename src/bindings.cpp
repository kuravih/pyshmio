#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include <chrono>
#include "shmio/shared_memory.hpp"

namespace py = pybind11;

inline py::object timespec_to_datetime(const timespec &_ts)
{
    using namespace std::chrono;
    auto ns = seconds(_ts.tv_sec) + nanoseconds(_ts.tv_nsec);
    auto tp = time_point<system_clock>(duration_cast<system_clock::duration>(ns));
    return py::cast(tp);
}

inline py::object keyword_get_name(const shmio::Keyword &_keyword)
{
    return py::cast(_keyword.name);
}

inline py::object keyword_get_comment(const shmio::Keyword &_keyword)
{
    return py::cast(_keyword.comment);
}

inline py::object keyword_get_value(const shmio::Keyword &_keyword)
{
    switch (_keyword.type)
    {
    case shmio::KeywordType::LONG:
        return py::cast(_keyword.value.numl);
    case shmio::KeywordType::DOUBLE:
        return py::cast(_keyword.value.numf);
    case shmio::KeywordType::STRING:
        return py::cast(std::string(_keyword.value.valstr));
    default:
        return py::none();
    }
}

inline void keyword_set_value(shmio::Keyword &_keyword, const py::object &_value)
{
    switch (_keyword.type)
    {
    case shmio::KeywordType::LONG:
        _keyword.value.numl = _value.cast<long>();
        break;
    case shmio::KeywordType::DOUBLE:
        _keyword.value.numf = _value.cast<double>();
        break;
    case shmio::KeywordType::STRING:
    {
        std::string s = _value.cast<std::string>();
        std::strncpy(_keyword.value.valstr, s.c_str(), sizeof(_keyword.value.valstr) - 1);
        _keyword.value.valstr[sizeof(_keyword.value.valstr) - 1] = '\0';
        break;
    }
    default:
        throw std::runtime_error("Invalid keyword type");
    }
}

class PySharedMemory
{
private:
    shmio::SharedMemory memory;

public:
    PySharedMemory() = default;
    PySharedMemory(const PySharedMemory &) = delete;
    PySharedMemory &operator=(const PySharedMemory &) = delete;
    PySharedMemory(PySharedMemory &&) noexcept = default;
    PySharedMemory &operator=(PySharedMemory &&) noexcept = default;

    // Open existing
    PySharedMemory(const std::string &_name)
    {
        if (shmio::open_shared_memory(memory, _name.c_str()) != 0)
        {
            throw std::runtime_error("Failed to open shared memory: " + _name);
        }
    }

    // Factory: create new
    static PySharedMemory create(const std::string &_name, const size_t _npx, const shmio::DataType _dtype, const std::vector<shmio::Keyword> &_keywords = {})
    {
        PySharedMemory wrapper;
        if (shmio::create_shared_memory(wrapper.memory, _name.c_str(), _npx, _dtype, _keywords) != 0)
        {
            throw std::runtime_error("Failed to create shared memory: " + _name);
        }
        return std::move(wrapper); // force move instead of copy
    }

    py::dict keywords_dict()
    {
        py::dict dict;
        for (const shmio::Keyword &keyword : get_keywords(memory))
        {
            dict[keyword.name] = keyword; // will be exposed as Keyword class
        }
        return dict;
    }

    std::string get_name() const
    {
        return memory.name;
    }

    size_t get_size() const
    {
        return memory.size;
    }

    py::object get_creation_time()
    {
        shmio::SharedStorage *storage = shmio::get_storage_ptr(memory);
        return timespec_to_datetime(storage->creationtime);
    }

    py::object get_last_access_time()
    {
        shmio::SharedStorage *storage = shmio::get_storage_ptr(memory);
        return timespec_to_datetime(storage->lastaccesstime);
    }

    void lock()
    {
        if (shmio::lock(shmio::get_storage_ptr(memory)) != 0)
        {
            throw std::runtime_error("pthread_mutex_lock failed");
        }
    }

    void unlock()
    {
        if (shmio::unlock(shmio::get_storage_ptr(memory)) != 0)
        {
            throw std::runtime_error("pthread_mutex_unlock failed");
        }
    }

    int consumer_request_start()
    {
        return shmio::consumer_request_start(shmio::get_storage_ptr(memory));
    }

    int consumer_wait_for_ready()
    {
        pybind11::gil_scoped_release release;
        return shmio::consumer_wait_for_ready(shmio::get_storage_ptr(memory));
    }

    int producer_wait_for_request()
    {
        pybind11::gil_scoped_release release;
        return shmio::producer_wait_for_request(shmio::get_storage_ptr(memory));
    }

    int producer_request_done()
    {
        return shmio::producer_request_done(shmio::get_storage_ptr(memory));
    }

    py::array ndarray()
    {
        shmio::SharedStorage *storage = shmio::get_storage_ptr(memory);

        uint32_t npx = storage->npx;
        shmio::DataType dtype = storage->dtype;

        std::string fmt;
        size_t elsize = shmio::DataTypeSize(dtype);

        switch (dtype)
        {
        case shmio::DataType::UINT8:
            fmt = py::format_descriptor<uint8_t>::format();
            break;
        case shmio::DataType::INT8:
            fmt = py::format_descriptor<int8_t>::format();
            break;
        case shmio::DataType::UINT16:
            fmt = py::format_descriptor<uint16_t>::format();
            break;
        case shmio::DataType::INT16:
            fmt = py::format_descriptor<int16_t>::format();
            break;
        case shmio::DataType::UINT32:
            fmt = py::format_descriptor<uint32_t>::format();
            break;
        case shmio::DataType::INT32:
            fmt = py::format_descriptor<int32_t>::format();
            break;
        case shmio::DataType::UINT64:
            fmt = py::format_descriptor<uint64_t>::format();
            break;
        case shmio::DataType::INT64:
            fmt = py::format_descriptor<int64_t>::format();
            break;
        // case shmio::DataType::HALF:
        //     fmt = py::format_descriptor<uint8_t>::format();
        //     break;
        case shmio::DataType::FLOAT:
            fmt = py::format_descriptor<float_t>::format();
            break;
        case shmio::DataType::DOUBLE:
            fmt = py::format_descriptor<double_t>::format();
            break;
        // case shmio::DataType::COMPLEX_FLOAT:
        //     fmt = py::format_descriptor<uint8_t>::format();
        //     break;
        // case shmio::DataType::COMPLEX_DOUBLE:
        //     fmt = py::format_descriptor<uint8_t>::format();
        //     break;
        default:
            throw std::runtime_error("Unsupported dtype");
        }
        py::object base = py::cast(this);
        py::array arr(py::buffer_info(shmio::get_pixels_ptr(memory), elsize, fmt, 1, {npx}, {elsize}), base);
        arr.mutable_data();
        return arr;
    }

    ~PySharedMemory()
    {
        shmio::close_shared_memory(memory);
    }
};

PYBIND11_MODULE(pyshmio, m)
{
    py::enum_<shmio::DataType>(m, "DataType")
        .value("UINT8", shmio::DataType::UINT8)
        .value("INT8", shmio::DataType::INT8)
        .value("UINT16", shmio::DataType::UINT16)
        .value("INT16", shmio::DataType::INT16)
        .value("UINT32", shmio::DataType::UINT32)
        .value("INT32", shmio::DataType::INT32)
        .value("UINT64", shmio::DataType::UINT64)
        .value("INT64", shmio::DataType::INT64)
        .value("HALF", shmio::DataType::HALF)
        .value("FLOAT", shmio::DataType::FLOAT)
        .value("DOUBLE", shmio::DataType::DOUBLE)
        .value("COMPLEX_FLOAT", shmio::DataType::COMPLEX_FLOAT)
        .value("COMPLEX_DOUBLE", shmio::DataType::COMPLEX_DOUBLE);

    py::enum_<shmio::KeywordType>(m, "KeywordType")
        .value("LONG", shmio::KeywordType::LONG)
        .value("DOUBLE", shmio::KeywordType::DOUBLE)
        .value("STRING", shmio::KeywordType::STRING);

    py::class_<shmio::Keyword>(m, "Keyword")
        // constructors
        .def(py::init<const char *, shmio::KeywordType, int64_t, const char *>(), py::arg("name"), py::arg("type"), py::arg("value"), py::arg("comment"))
        .def(py::init<const char *, shmio::KeywordType, double, const char *>(), py::arg("name"), py::arg("type"), py::arg("value"), py::arg("comment"))
        .def(py::init<const char *, shmio::KeywordType, const char *, const char *>(), py::arg("name"), py::arg("type"), py::arg("value"), py::arg("comment"))
        // properties
        .def_property_readonly("name", &keyword_get_name)
        .def_property_readonly("comment", &keyword_get_comment)
        .def_readonly("type", &shmio::Keyword::type)
        .def_property("value", &keyword_get_value, &keyword_set_value);

    py::class_<PySharedMemory>(m, "SharedMemory")
        .def(py::init<const std::string &>(), py::arg("name"))
        .def_static("create", &PySharedMemory::create, py::arg("name"), py::arg("npx"), py::arg("dtype"), py::arg("keywords") = std::vector<shmio::Keyword>{})
        .def_property_readonly("creation_time", &PySharedMemory::get_creation_time)
        .def_property_readonly("last_access_time", &PySharedMemory::get_last_access_time)
        .def_property_readonly("size", &PySharedMemory::get_size)
        .def_property_readonly("name", &PySharedMemory::get_name)
        .def_property_readonly("keywords", &PySharedMemory::keywords_dict)
        .def("lock", &PySharedMemory::lock)
        .def("unlock", &PySharedMemory::unlock)
        .def("consumer_request_start", &PySharedMemory::consumer_request_start)
        .def("consumer_wait_for_ready", &PySharedMemory::consumer_wait_for_ready)
        .def("producer_wait_for_request", &PySharedMemory::producer_wait_for_request)
        .def("producer_request_done", &PySharedMemory::producer_request_done)
        .def_property_readonly("ndarray", &PySharedMemory::ndarray);
}
