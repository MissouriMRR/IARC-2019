#include "realsense.hpp"
#include <iostream>

#define RETURN_NONE()       \
    {                       \
        Py_IncRef(Py_None); \
        return Py_None;     \
    }

class Pixel
{
  private:
    int m_x;
    int m_y;
    float pixel[2];
    cv::Mat *m_src;

  public:
    Pixel(int x, int y, cv::Mat *src)
        : m_x(std::max(0, std::min(x, src->cols))),
          m_y(std::max(0, std::min(y, src->rows))),
          m_src(src)
    {
        pixel[0] = m_x;
        pixel[1] = m_y;
    }

    bool operator==(const Pixel &rhs) const
    {
        return m_x == rhs.m_x && m_y == rhs.m_y;
    }

    bool operator!=(const Pixel &rhs) const
    {
        return !((*this) == rhs);
    }

    int x() const
    {
        return m_x;
    }

    int y() const
    {
        return m_y;
    }

    uint16_t get() const
    {
        return m_src->at<uint16_t>(m_y, m_x);
    }

    void neighbors(std::vector<std::pair<int, int>> &neighbors, uint16_t exclude) const
    {
        neighbors.clear();

        std::array<std::pair<int, int>, 8> res{
            std::pair<int, int>{m_x - 1, m_y - 1},
            std::pair<int, int>{m_x, m_y - 1},
            std::pair<int, int>{m_x + 1, m_y - 1},
            std::pair<int, int>{m_x + 1, m_y},
            std::pair<int, int>{m_x + 1, m_y + 1},
            std::pair<int, int>{m_x, m_y + 1},
            std::pair<int, int>{m_x - 1, m_y + 1},
            std::pair<int, int>{m_x - 1, m_y}};

        for (auto &&point : res)
        {
            if ((0 <= point.first < m_src->cols - 1 && 0 <= point.second < m_src->rows - 1) &&
                (m_src->at<uint16_t>(point.second, point.first) != exclude))
            {
                neighbors.emplace_back(point.first, point.second);
            }
        }
    }
};

static std::atomic_bool alive{true};
static std::thread *video_processing_thread_reference = nullptr;

Realsense::Realsense() : m_disparity_to_depth(false), m_align_to(RS2_STREAM_DEPTH), m_has_begun(false)
{
    // fills all zero pixels (TODO: use a more accurate estimator for this)
    m_spatial.set_option(RS2_OPTION_HOLES_FILL, 5);
    // enable depth stream
    m_config.enable_stream(RS2_STREAM_DEPTH);
    // enable color stream and use RGBA to enable blending
    m_config.enable_stream(RS2_STREAM_COLOR, RS2_FORMAT_RGBA8);

    m_profile = m_pipe.start(m_config);

    auto sensor = m_profile.get_device().first<rs2::depth_sensor>();

    auto range = sensor.get_option_range(RS2_OPTION_VISUAL_PRESET);

    for (auto i = range.min; i < range.max; i += range.step)
        if (std::string(sensor.get_option_value_description(RS2_OPTION_VISUAL_PRESET, i)) == "High Density")
            sensor.set_option(RS2_OPTION_VISUAL_PRESET, i);
}

void Realsense::begin()
{
    static std::thread video_processing_thread([&]() {
        rs2::processing_block frame_processor([&](rs2::frameset data,
                                                  rs2::frame_source &source) {
            data = data.apply_filter(m_align_to);
            data = data.apply_filter(m_decimator);
            data = data.apply_filter(m_depth_to_disparity);
            data = data.apply_filter(m_spatial);
            data = data.apply_filter(m_temporal);
            data = data.apply_filter(m_disparity_to_depth);
            m_raw_depth_queue.enqueue(data.get_depth_frame());
            data = data.apply_filter(m_color_map);
            source.frame_ready(data);
        });

        frame_processor >> m_queue;

        while (alive)
        {
            rs2::frameset frameset;
            if (m_pipe.poll_for_frames(&frameset))
                frame_processor.invoke(frameset);
        }
    });

    video_processing_thread_reference = &video_processing_thread;
}

PyObject *Realsense::depth()
{

    if (alive)
    {
        m_queue.poll_for_frame(&m_current);

        if (m_current)
        {
            auto depth = m_current.get_depth_frame();
            auto color = m_current.get_color_frame();
            auto colorized_depth = m_current.first(RS2_STREAM_DEPTH, RS2_FORMAT_RGB8);
            const int w = colorized_depth.as<rs2::video_frame>().get_width();
            const int h = colorized_depth.as<rs2::video_frame>().get_height();

            cv::Mat depth_image(cv::Size(w, h), CV_8UC3, (void *)colorized_depth.get_data(), cv::Mat::AUTO_STEP);
            return pyopencv_from(depth_image);
        }
    }

    RETURN_NONE();
}
/*
PyObject *Realsense::blobs(int num_blobs, int min_area, double min_depth, double max_depth, double margin, double tolerance)
{
    if (alive)
    {
        rs2::frame raw_depth;
        const auto depth_scale = get_depth_scale();

        if (m_raw_depth_queue.poll_for_frame(&raw_depth))
        {
            const auto &depth_frame = raw_depth.as<rs2::depth_frame>();
            const int w = depth_frame.get_width();
            const int h = depth_frame.get_height();
            cv::Mat depth(cv::Size(w, h), CV_16UC1, (void *)raw_depth.get_data(), cv::Mat::AUTO_STEP);
            cv::Mat buffer(cv::Size(w, h), CV_16UC1, Scalar(0));
            cv::Mat result(cv::Size(w, h), CV_32FC1, Scalar(0));
            const uint16_t *p_depth_data = reinterpret_cast<const uint16_t *>(depth_frame.get_data());
            uint16_t *p_depth_data_copy = depth.ptr<uint16_t>();
            const uint16_t INVALID_DEPTH = std::numeric_limits<uint16_t>::max();

            int blobs_found = 0;

#pragma omp parallel for schedule(dynamic)
            for (int y = 0; y < h; ++y)
            {
                auto depth_pixel_index = y * w;

                for (int x = 0; x < w; ++x, ++depth_pixel_index)
                {
                    auto pixels_distance = depth_scale * p_depth_data[depth_pixel_index];

                    if ((pixels_distance <= min_depth || pixels_distance >= max_depth) ||
                        (x < w * margin || x > w * (1 - margin)) ||
                        (y < h * margin || y > h * (1 - margin)))
                    {
                        p_depth_data_copy[depth_pixel_index] = INVALID_DEPTH;
                    }
                }
            }

            while (blobs_found < num_blobs && cv::countNonZero(depth) >= min_area)
            {
                buffer = 0;

                double min, max;
                cv::Point min_loc, max_loc;
                cv::minMaxLoc(depth, &min, &max, &min_loc, &max_loc);

                if (min == INVALID_DEPTH)
                {
                    break;
                }

                Pixel minimum(min_loc.x, min_loc.y, &depth);
                std::vector<std::pair<int, int>> neighbors;
                std::map<int, bool> visited;
                std::queue<Pixel> candidate_vertices;

                buffer.at<uint16_t>(min_loc.y, min_loc.x) = ~((uint16_t)0);
                auto get_index = [&](int x, int y) -> int {
                    return y * w + x;
                };

                visited[get_index(min_loc.x, min_loc.y)] = true;
                candidate_vertices.push(minimum);

                while (candidate_vertices.size() > 0)
                {
                    const Pixel &pixel_current = candidate_vertices.front();
                    const auto current_pixel_distance = pixel_current.get() * depth_scale;
                    pixel_current.neighbors(neighbors, INVALID_DEPTH);

                    for (auto &&neighbor : neighbors)
                    {
                        auto found_element = visited.find(get_index(neighbor.first, neighbor.second));
                        if (found_element == visited.end())
                        {
                            auto neighbor_distance = depth.at<uint16_t>(neighbor.second, neighbor.first) * depth_scale;
                            if (static_cast<double>(std::fabs(neighbor_distance - current_pixel_distance)) <= tolerance)
                            {
                                buffer.at<uint16_t>(neighbor.second, neighbor.first) = ~((uint16_t)0);
                                visited[get_index(neighbor.first, neighbor.second)] = true;
                                candidate_vertices.emplace(neighbor.second, neighbor.first, &depth);
                            }
                        }
                    }

                    candidate_vertices.pop();
                }

                visited.clear();

                std::cout << cv::countNonZero(buffer) << std::endl;

                if (cv::countNonZero(buffer) >= min_area)
                {
                    ++blobs_found;
                }

                depth = depth & ~buffer;
            }

            if (!blobs_found)
            {
                RETURN_NONE();
            }

            buffer.convertTo(result, CV_32FC1);
            return pyopencv_from(result);
        }
    }

    RETURN_NONE();
}
*/

PyObject *Realsense::color()
{
    if (alive)
    {
        m_queue.poll_for_frame(&m_current);

        if (m_current)
        {
            auto color = m_current.get_color_frame();
            const int w = color.as<rs2::video_frame>().get_width();
            const int h = color.as<rs2::video_frame>().get_height();

            cv::Mat color_image(cv::Size(w, h), CV_8UC4, (void *)color.get_data(), cv::Mat::AUTO_STEP);
            cv::cvtColor(color_image, color_image, cv::COLOR_RGBA2BGR);
            return pyopencv_from(color_image);
        }
    }

    RETURN_NONE();
}

float Realsense::get_depth_scale()
{
    for (rs2::sensor &sensor : m_profile.get_device().query_sensors())
    {
        if (rs2::depth_sensor depth_sensor = sensor.as<rs2::depth_sensor>())
        {
            return depth_sensor.get_depth_scale();
        }
    }
}

void Realsense::shutdown()
{
    if (video_processing_thread_reference)
    {
        alive = false;
        video_processing_thread_reference->join();
    }
}

Realsense::~Realsense()
{
    shutdown();
}