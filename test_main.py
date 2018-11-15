import unittest
import utility

class TestUtility(unittest.TestCase):
	def setUp(self):
		print("Starting the tests")

	def test_findFilenameSubstr(self):

		self.assertEqual(utility.getFilenameSubstr("C:/hallo/welt.txt"), "welt.txt")
		self.assertEqual(utility.getFilenameSubstr("hallo/welt.txt"), "welt.txt")
		self.assertEqual(utility.getFilenameSubstr("welt.txt"), "welt.txt")
		self.assertEqual(utility.getFilenameSubstr("C:\\hallo\\welt.txt"), "welt.txt")

		self.assertEqual(utility.getFilenameSubstr("C:/hallo/welt.json"), "welt.json")
		self.assertEqual(utility.getFilenameSubstr("hallo/welt.json"), "welt.json")
		self.assertEqual(utility.getFilenameSubstr("welt.json"), "welt.json")
		self.assertEqual(utility.getFilenameSubstr("C:\\hallo\\welt.json"), "welt.json")
