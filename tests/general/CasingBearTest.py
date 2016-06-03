from queue import Queue
from bears.general.CasingBear import CasingBear
from bears.general.AnnotationBear import AnnotationBear
from tests.LocalBearTestHelper import LocalBearTestHelper
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting
from coalib.bears.LocalBear import LocalBear


class CasingBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section("test section")

    def get_results(self, file, section=None):
        self.dep_uut = AnnotationBear(section, Queue())
        dep_results_valid = self.dep_uut.execute("file", file)
        uut = CasingBear(section, Queue())

        if dep_results_valid == None:
            dep_results_valid = []
        arg_dict = {'dependency_results':
                    {AnnotationBear.__name__:
                     list(dep_results_valid)},
                    'file': file}
        reply = uut.run_bear_from_section(["file"], arg_dict)
        return list(reply)

    def verify_bear(self,
                    file=None,
                    valid=True,
                    exception=False):
        if valid and not exception:
            valid_results = self.get_results(file, self.section)
            self.assertEqual(valid_results, [])
        elif not valid and not exception:
            invalid_results = self.get_results(file, self.section)
            self.assertNotEqual(invalid_results, [])
        else:
            with self.assertRaises(FileNotFoundError) as cm:
                invalid_results = self.get_results(file, self.section)

    def test_defaults(self):
        self.section.append(Setting("casing", "snake"))
        self.section.append(Setting("language", "CPP"))
        self.verify_bear(["int abc_def;\n", "int ab_cd;\n"])
        self.verify_bear(["int abc_def = xyz_abc;\n"])
        self.verify_bear(["int abcEfg = 4;\n"], valid=False)
        self.verify_bear(["int abCd = 4;\n"], valid=False)
        self.verify_bear(
            ["int abc_def;\n", "int abCd;\n"],
            valid=False)
        self.verify_bear(
            ["char wrongStr=\"test\";\n", "int correct_var = 42;\n"],
            valid=False)
        self.verify_bear(
            ["char correct_str=\"test\";\n", "int correct_var = 42;\n"],
            valid=True)
        self.verify_bear(
            ["testVar = 42;\n", "testVar = 0;\n", "testVar += 1;\n"],
            valid=False)
        self.verify_bear(
            ["int incorrectVar = 32, anotherInt = 22\n"],
            valid=False)
        self.verify_bear(
            ["int correct_var = 32, anotherInt = 22\n"],
            valid=False)
        self.verify_bear(
            ["int correct_var = 32, another_int = 22\n"],
            valid=True)

    def test_invalid_settings(self):
        self.section = Section("test_section_2")
        self.section.append(Setting("casing", "snake"))
        self.section.append(Setting("language", "InvalidLang"))

        self.verify_bear(
            ["int testVar = 42;\n", "int correct_var = 32;\n"],
            exception=True)

        self.section = Section("test_section_3")
        self.section.append(Setting("casing", "invalid"))
        self.section.append(Setting("language", "C"))

        # This should return no results since the given casing is invalid.
        self.verify_bear(
            ["int testVar = 42;\n"],
            valid=True)

        self.section = Section("test_section_4")
        self.section.append(Setting("casing", "snake"))
        self.section.append(Setting("language", "python3"))

        # No results will be returned since python3 doesn't have
        # complete coalang support with keywords yet.
        self.verify_bear(
            ["testVar = 42\n"],
            valid=True)
