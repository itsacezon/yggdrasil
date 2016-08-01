yggdrasil
=========

Acezon Cay


Description
-----------

Yggdrasil is a simple command-line tool for creating decision trees
based on the ID3 algorithm. It comes in two pieces (commands):

+ `train` takes in an XML file (see [test](../master/test)
for the format) and creates a `.tree` file that will be used
for testing accuracy and/or querying information.
+ `test` takes in the `.tree` file created in `train` and an XML file
(with `type="testing"`), and displays the accuracy of the decision tree.
It can also query the decision tree by putting parameters
specified in the XML file.


Requirements
------------

+ Python >= 2.7
