import graphviz
import pydot

# Erstelle ein neues Graph-Objekt
graph = pydot.Dot(graph_type='digraph', rankdir='LR')

# Füge die Klasse als Knoten hinzu
label = '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
  <TR><TD COLSPAN="2"><B>Person</B></TD></TR>
  <TR><TD ALIGN="LEFT">- name</TD><TD>str</TD></TR>
  <TR><TD ALIGN="LEFT">- age</TD><TD>int</TD></TR>
  <TR><TD ALIGN="LEFT">+ greet()</TD><TD>method</TD></TR>
</TABLE>>'''

node = pydot.Node("Person", shape="plaintext", label=label)
graph.add_node(node)

dot_string = graph.to_string()
print(dot_string)
# Speichere als PNG
#graph.write_txt("./person_class.txt")
