from xml.etree.ElementTree import parse as parse_xml


def parse_config(filename):
    """
    Reads xml config file and returns parsed data.

    Parameters
    ----------
    filename: str
        Filename of desired config file.

    Returns
    -------
    list of parsed graphs
        Parsed data in format [{graph}, {graph}]. The graph dictionary includes output, legend, title, xlabel, ylabel
        and metrics. Metrics is a list of dictionaries including label, color, func, x_stream, y_stream and z_stream.
    """

    output = []

    root = parse_xml(filename).getroot()

    for graph in root.findall('graph'):
        output.append({
            'output': graph.get('output'),
            'legend': graph.get('legend'),

            'title': graph.get('title'),
            'xlabel': graph.get('xlabel'),
            'ylabel': graph.get('ylabel'),

            'metrics': []
        })

        for metric in graph.findall('metric'):
            output[-1]['metrics'].append({
                'label': metric.get('label'),

                'color': metric.get('color'),

                'func': metric.get("func"),

                'x_stream': metric.get('x_stream'),
                'y_stream': metric.get('y_stream'),
                'z_stream': metric.get('z_stream')
            })

    return output
