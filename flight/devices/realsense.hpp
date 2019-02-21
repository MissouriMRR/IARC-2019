#ifndef REALSENSE_HPP
#define REALSENSE_HPP

#include "conversion.hpp"

#include <librealsense2/rs.hpp>
#include <librealsense2/rsutil.h>

#include <atomic>
#include <thread>
#include <mutex>

class Realsense
{
  private:
    rs2::colorizer m_color_map;
    rs2::decimation_filter m_decimator;
    rs2::disparity_transform m_depth_to_disparity;
    rs2::disparity_transform m_disparity_to_depth;
    rs2::spatial_filter m_spatial;
    rs2::temporal_filter m_temporal;
    rs2::align m_align_to;
    rs2::pipeline m_pipe;
    rs2::config m_config;

    rs2::pipeline_profile m_profile;
    rs2::frame_queue m_queue;
    rs2::frameset m_current;

    bool m_has_begun;

    void shutdown();

  public:
    Realsense();
    void begin();
    PyObject *depth();
    PyObject *color();
    virtual ~Realsense();
};

#endif