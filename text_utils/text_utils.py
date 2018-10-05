import string, re, unicodedata

# Symbol for shape of empty string
null_shape = "null"

# Valid ASCII characters (not including whitespace)
valid_chars = string.ascii_letters + string.digits + string.punctuation

def unicode_to_ASCII(s):
    """ Turn a Unicode string to plain ASCII, based on http://stackoverflow.com/a/518232/2809427 """
    norm = s
    
    # Normalize curly quotes
    norm = re.sub("’", "'", norm)
    norm = re.sub("[”“]", "\"", norm)

    # Map non-ASCII chars to ASCII base form, remove combining
    # characters, and remove any remaining unwanted characters
    # (characters that could not be converted to ASCII, whitespace,
    # etc.)
    norm = ''.join(
        c for c in unicodedata.normalize('NFD', norm)
        if unicodedata.category(c) != 'Mn'
        and c in valid_chars
    )
    return norm

def get_word_shape(word, normalize=True, max_repeats=-1):
    """Get word shape. ASCII chars are replaced by 'x' if lower case or
    'X' if upper case, and digits are replaced by '9'. All other
    characters remain as they are. 

    If normalize is True, the word is first converted to ASCII.

    If max_repeats > -1, the shape is squeezed by removing symbols
    that are repeated more that max_repeats times.
    """
    if not len(word):
        return null_shape
    # Normalize characters by converting to ASCII
    if normalize:
        norm = unicode_to_ASCII(word)
        # If normalization returned empty string, return null shape
        if not len(norm):
            return null_shape
    else: 
        norm = word
    shape = norm
    shape = re.sub("[A-Z]", "X", shape)
    shape = re.sub("[a-z]", "x", shape)
    shape = re.sub("[0-9]", "9", shape)
    if max_repeats > -1:
        shape = squeeze_string(shape, max_repeats=max_repeats)
    return shape

def squeeze_string(word, max_repeats=0):
    """ Remove repeated characters in string. """
    squeezed = ""
    prev = None
    nb_repeats = 0
    for char in word:
        if char == prev:
            nb_repeats += 1
        else:
            nb_repeats = 0
        if nb_repeats <= max_repeats:
            squeezed += char
        prev = char
    return squeezed
