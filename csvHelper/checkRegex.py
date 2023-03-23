import re

def replace_lookahead_and_backrefs(pattern):
    # Replace positive lookahead (?=...)
    pattern = re.sub(r'\(\?=(.+?)\)', r'\1', pattern)

    # Replace negative lookahead (?!...)
    pattern = re.sub(r'\(\?!([^)]+)\)', r'\1', pattern)

    # Replace backreferences (\1, \2, ...)
    pattern = re.sub(r'\\(\d+)', r'(group\1)', pattern)

    return pattern

original_pattern1 = "?=example"
new_pattern1 = replace_lookahead_and_backrefs(original_pattern1)
original_pattern2 = "(?!example)"
new_pattern2 = replace_lookahead_and_backrefs(original_pattern2)
original_pattern3 = "(group1)(group2)\\1"
new_pattern3 = replace_lookahead_and_backrefs(original_pattern3)

print("Original pattern:", original_pattern1)
print("New pattern:", new_pattern1)
print("Original pattern:", original_pattern2)
print("New pattern:", new_pattern2)
print("Original pattern:", original_pattern3)
print("New pattern:", new_pattern3)