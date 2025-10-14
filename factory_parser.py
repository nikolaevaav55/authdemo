class Factory:
    @staticmethod
    def build_sequence():
        """Creates and returns an empty list"""
        return []
    
    @staticmethod
    def build_number(string):
        """Converts string to integer and returns the result"""
        return int(string.strip())


class Loader:
    @staticmethod
    def parse_format(string, factory):
        seq = factory.build_sequence()
        for sub in string.split(","):
            item = factory.build_number(sub)
            seq.append(item)

        return seq


# Test the implementation
if __name__ == "__main__":
    # Test with the provided example
    res = Loader.parse_format("4, 5, -6", Factory)
    print(f"Result: {res}")
    print(f"Expected: [4, 5, -6]")
    print(f"Test passed: {res == [4, 5, -6]}")
    
    # Additional tests
    print("\nAdditional tests:")
    
    # Test with single number
    res2 = Loader.parse_format("42", Factory)
    print(f"Single number test: {res2} == [42]: {res2 == [42]}")
    
    # Test with zeros and negative numbers
    res3 = Loader.parse_format("0, -1, 100", Factory)
    print(f"Zero and negative test: {res3} == [0, -1, 100]: {res3 == [0, -1, 100]}")
    
    # Test with extra spaces
    res4 = Loader.parse_format("  1  ,  2  ,  3  ", Factory)
    print(f"Extra spaces test: {res4} == [1, 2, 3]: {res4 == [1, 2, 3]}")