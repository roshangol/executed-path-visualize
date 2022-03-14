import html

import graphviz as gv

FONT_SIZE = "22"
PEN_WIDTH = "2"


def build_node_template(node_label, contents):
    content = node_content_to_html(contents.splitlines())
    b_len = len(contents.splitlines())
    line_height = 40
    s = f"""<<FONT POINT-SIZE="{FONT_SIZE}">  
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <tr>
                <td width="30" height="30" fixedsize="true">{node_label}</td>
                <td width="9" height="9" fixedsize="true" style="invis"></td>
                <td width="9" height="9" fixedsize="true" style="invis"></td>
            </tr>
            <tr>
                <td width="30" height="{b_len * line_height}" fixedsize="true" sides="tlb"></td>
                <td width="50" height="{b_len * line_height}" fixedsize="false" sides="bt" PORT="here">{content}</td>
                <td width="30" height="{b_len * line_height}" fixedsize="true" sides="brt"></td>
            </tr>
        </TABLE>
    </FONT>>"""
    return strip_lines(s)


def strip_lines(x: str): return "\n".join(line.strip() for line in x.splitlines())


def concatenate_list_data(list):
    result = ''
    for element in list:
        result = result + "\n" + str(element)
    return result

def node_content_to_html(node_contents):
    delimiter = '<br align="left"/>\n'
    content_list_string = delimiter.join([html.escape(f"{content}") for content in node_contents])
    return content_list_string + delimiter
