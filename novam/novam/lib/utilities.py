import unicodedata, re

# From http://stackoverflow.com/questions/92438/\
# stripping-non-printable-characters-from-a-string-in-python:

control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))

def strip_control_chars(s):
	return control_char_re.sub('', s)
