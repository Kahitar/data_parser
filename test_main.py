import unittest
import main

class TestMain(unittest.TestCase):
	def setUp(self):
		print("Starting the tests")

	def test_findFilenameSubstr(self):

		self.assertEqual(main.findFilenameSubstr("C:/hallo/welt.txt"), "welt.txt")
		self.assertEqual(main.findFilenameSubstr("hallo/welt.txt"), "welt.txt")
		self.assertEqual(main.findFilenameSubstr("welt.txt"), "welt.txt")
		self.assertEqual(main.findFilenameSubstr("C:\\hallo\\welt.txt"), "welt.txt")