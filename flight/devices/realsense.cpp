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