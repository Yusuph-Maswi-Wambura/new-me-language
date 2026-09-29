import unittest

from novalang import NovaError, run


class NovaLangTests(unittest.TestCase):
    def test_functions_and_recursion(self):
        source = """
        fn fibonacci(n) { if (n < 2) { return n; } return fibonacci(n - 1) + fibonacci(n - 2); }
        print(fibonacci(8));
        """
        self.assertEqual(run(source), ["21"])

    def test_scope_arrays_and_loop(self):
        source = """
        let values = [2, 4, 6]; let total = 0; let index = 0;
        while (index < length(values)) { let item = values[index]; total = total + item; index = index + 1; }
        print(total);
        """
        self.assertEqual(run(source), ["12"])

    def test_errors_are_user_facing(self):
        with self.assertRaisesRegex(NovaError, "Undefined variable"):
            run("print(missing);")

    def test_else_if_and_break(self):
        source = """
        let index = 0;
        while (true) {
            if (index == 0) { print("zero"); }
            else if (index == 1) { print("one"); }
            else { break; }
            index = index + 1;
        }
        """
        self.assertEqual(run(source), ["zero", "one"])

    def test_for_loops_maps_and_indexed_assignment(self):
        source = """
        let profile = {name: "Ada", score: 0};
        for (let index = 0; index < 3; index = index + 1) {
            profile["score"] = profile["score"] + index;
        }
        print(profile["name"], profile["score"], has(profile, "name"));
        """
        self.assertEqual(run(source), ["Ada 3 true"])

    def test_classes_instances_and_inheritance(self):
        source = """
        class Animal {
            fn init(name) { this.name = name; }
            fn speak() { return this.name; }
        }
        class Dog < Animal {
            fn speak() { return super.speak() + " says woof"; }
        }
        let dog = Dog("Milo");
        print(dog.speak());
        """
        self.assertEqual(run(source), ["Milo says woof"])

    def test_functional_helpers_sets_match_and_errors(self):
        source = """
        let doubled = map(lambda(value) { return value * 2; }, [1, 2, 3]);
        let unique = set([1, 1, 2, 3]);
        match (length(doubled)) {
            case 3: { print("mapped", doubled[1]); }
            default: { print("wrong"); }
        }
        try { throw "planned failure"; } catch (error) { print(error); } finally { print("cleaned"); }
        print(contains(unique, 2), nil ?? "fallback");
        """
        self.assertEqual(run(source), ["mapped 4", "planned failure", "cleaned", "true fallback"])


if __name__ == "__main__":
    unittest.main()
