Dear User,

please, follow these instructions on how to run the "Program.jar" using the Voice Recognition feature.


1. Prerequisites:

1a.
Make sure your sound-card and headset is working (both earphones and microphone).
1b.
Check if you already have Java Runtime Environment and Apache Ant installed, by typing in your terminal/console:
java -version
ant -version
1c.
If you get a version number printed, go on with 2. Installation.
If not, you need to install it.
- JRE, version 6.0 or higher, download from:
http://www.oracle.com/technetwork/indexes/downloads/index.html
- Ant 1.6.0 or higher, Apache Ant download from:https:
//www.apache.org/dist/ant/binaries/
- APACHE Ant install manual: http://ant.apache.org/manual/install.html

2. Installation
2a.
Download the files "TestPath.jar" and "Program.jar"
2b.
Run in terminal/console:
java -jar TestPath.jar
This will print your home path.
2c.
Copy the file Program.jar into your home path and extract into the folder "TaxProgram"(for linux and Mac Users type: unzip Program.jar -d TaxProgram)

3. How to run the program basics - use test input file
Go into your home directory and run in terminal/console:
java -jar Program.jar
Select your data type of the drop down list: O or S, and press "Show Input Fields".

3a.
Mandatory inputs:
You need to define an input file including your sample names, font color, onButton, or listNr, and RecognitionName; to get an overview of this input file format, you can press "How to create Data File".
There is an input file "taxtext_x1.txt" prepared, which you may want to use for testing purposes.
If your inpu file was successfully read by the program, you will see the file content on your terminal/console output.
Press "Start Counting".
Normal counting by mouse will work by pressing the buttons listed at the top or choose one of the names from the drop down list.

3b.
Use the voice recognition feature
- Press "Save data for other count mode"
- Press "Voice Recognition"
- Press "Phoneme" to check the list of allowed phonemes (sounds), this is just as additional information; press "OK" to get the voice recognition module started.
- If you used the test input file "taxtext_x1.txt", you can go on with "Ready to speak"
- If you want to define your own customized words, see 4. to see additional instructions
//- ... program crash with Ubuntu?? maybe need to re-write start command for Mac/Linux versions ...
//- run: java -mx256m -jar "/home/dorina/TaxProgram/bin/HelloWorld.jar"
- press "Load data from other count mode"
- press "Speak"
- at the bottom there is a text showing the actual status, and in the middle part you will see the word recognized
- make an intial sound (will not count) to initialize, the "Speak" button will get greyed out
- start speaking. If the voice recognition program detected a word, you will hear a sound as confirmation.
- If you want to have a break or stop, press "Pause Counting" (or say "stop" if you included that word in the grammar file)
- press "Save data for other count mode"
- press "Exit"; will close the voice recognition module
- go on with normal (mouse) counting
- press "Save Data" -> "open a File" to save your counts, choose an appropriate folder, and type in your file name after "File Name:"
//- redo "Save Data" -> "open a File" to save your counts

4. How to run the program advanced - use customized input files

There are two "system command" words, which you may want to include in your grammar file of allowed words (*.gram file); these are "remove" to remove the very last word recognized, and "stop" to stop the voice recognition.

4a.
- Press "Save data for other count mode"
- Press "Voice Recognition"
- Press "OK"
- Press "Open Files", this will open several files:
1) informative "CMU Pronouncing Dictionary" explanation will open in your browser,
2) default grammar text file "hello.gram" will open in text editor;
if you want to you edit this file, and change the list of allowed words;
if changed say "File"->"Save", if not: just close the file
3) default dictionary file "cmudict.0.6d" will open in text editor;
if you want to you edit this file, go to the file end, here you will see the dictionary definitions of the words used in the test input file;
to insert new words, just append your words and phonemes (sounds) at the end of the file;
if changed say "File"->"Save", if not: just close the file


