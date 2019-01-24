import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString


def xml_to_string(xml_tag):
    """
    Makes xml objects into string formatted in a readable way
    """
    return parseString(ET.tostring(xml_tag)).toprettyxml(indent="  ")


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

    #
    # Decode graph
    output = []

    root = ET.parse(filename).getroot()

    for graph in root.findall('graph'):
        output.append({
            'output': graph.get('output'),
            'legend': graph.get('legend'),

            'title': graph.get('title'),
            'xlabel': graph.get('xlabel'),
            'ylabel': graph.get('ylabel'),

            'lower_time': graph.get('lower_time'),
            'upper_time': graph.get('upper_time'),

            'metric': []
        })

        for metric in graph.findall('metric'):
            output[-1]['metric'].append({

                'label': metric.get('label'),

                'color': metric.get('color'),

                'func': metric.get("func"),

                'x_stream': metric.get('x_stream'),
                'y_stream': metric.get('y_stream'),
                'z_stream': metric.get('z_stream')
            })

    return output


def possible_metrics(filename):
    """
    Returns list of possible metrics and their data.

    Parameters
    ----------
    filename: str
        Filename to read possible metrics from.

    Returns
    -------
    List of possible metrics. List of dictionaries -> {label: [(x_stream, y_stream, z_stream), func]}
    """

    raw_data = parse_config(filename)

    metrics = {
        metric['label']: [(metric['x_stream'], metric['y_stream'], metric['z_stream']), metric['func']]
        for graph in raw_data for metric in graph['metric']}

    return metrics


def write_config(filename, data):
    """
    Writes config file in xml format.

    Parameters
    ----------
    filename: str
        Filename to be saved as.

    data: list of dictionaries
        List of graphs and all of their data.
    """

    # Encode data
    desiredgraphs = ET.Element('desiredgraphs')

    for graph in data:
        curr_graph = ET.SubElement(desiredgraphs, 'graph', {key: value for key, value in graph.items() if type(value) is not list and value})
        for key, lst in [(key, value) for key, value in graph.items() if type(value) is list and value]:
            for item in lst:
                ET.SubElement(curr_graph, key, {key: value for key, value in item.items() if value})

    # Write
    with open(filename, 'w') as g:
        g.write(xml_to_string(desiredgraphs))


if __name__ == '__main__':
    def test_parse_config():
        print(parse_config('test_config1.xml'))

    def test_write_config():
        write_config('test_config2.xml', parse_config('test_config1.xml'))

    def test_possible_metrics():
        print(possible_metrics('test_config1.xml'))

    test_possible_metrics()

