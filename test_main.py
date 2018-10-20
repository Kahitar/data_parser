import unittest
import utility

class TestUtility(unittest.TestCase):
	def setUp(self):
		print("Starting the tests")

	def test_findFilenameSubstr(self):

		self.assertEqual(utility.findFilenameSubstr("C:/hallo/welt.txt", 3), "welt.txt")
		self.assertEqual(utility.findFilenameSubstr("hallo/welt.txt", 3), "welt.txt")
		self.assertEqual(utility.findFilenameSubstr("welt.txt", 3), "welt.txt")
		self.assertEqual(utility.findFilenameSubstr("C:\\hallo\\welt.txt", 3), "welt.txt")

		self.assertEqual(utility.findFilenameSubstr("C:/hallo/welt.json", 4), "welt.json")
		self.assertEqual(utility.findFilenameSubstr("hallo/welt.json", 4), "welt.json")
		self.assertEqual(utility.findFilenameSubstr("welt.json", 4), "welt.json")
		self.assertEqual(utility.findFilenameSubstr("C:\\hallo\\welt.json", 4), "welt.json")