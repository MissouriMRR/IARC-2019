#ifndef REALSENSE_HPP
#define REALSENSE_HPP

#include "conversion.hpp"

#include <librealsense2/rs.hpp>
#include <librealsense2/rsutil.h>

#include <atomic>
#include <thread>
#include <mutex>
#include <array>
#include <set>
#include <algorithm>
#include <limits>
#include <utility>
#include <queue>
#include <map>

#define DEFAULT_MIN_AREA 100
#define D415_MIN_DETPH .3
#define D415_MAX_DEPTH 10
#define DEFAULT_MARGIN .05
#define DEFAULT_TOLERANCE 5

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
  rs2::frame_queue m_raw_depth_queue;
  rs2::frameset m_current;

  bool m_has_begun;

  void shutdown();

public:
  Realsense();
  void begin();
  PyObject *depth();
  PyObject *color();
  /*
  PyObject *blobs(int num_blobs = 1, int min_area = DEFAULT_MIN_AREA,
                  double min_depth = D415_MIN_DETPH, double max_depth = D415_MAX_DEPTH,
                  double margin = DEFAULT_MARGIN, double tolerance = DEFAULT_TOLERANCE);
  */
  float get_depth_scale();
  virtual ~Realsense();
};

#endif