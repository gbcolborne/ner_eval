

def get_mentions_from_BIO_file(path, encoding="BIO-2",
                               label_col=-1,
                               ignore_boundaries=False,
                               allow_prefix_errors=False,
                               allow_type_errors=False):
    """Given the path of a file containing named entity annotations in
    column text format (tokens in the first column, BIO-1 or BIO-2
    labels in the last column by default, empty lines between
    sentences), return list containing a (line_number, tokens, labels)
    tuple for each entity mention.

    encoding specifies the label encoding (BIO-1 or BIO-2).

    label_col specifies the index of the column containing the labels
    (zero-indexed, last column by default).

    If ignore_boundaries is set to True, then we ignore sentence boundaries,
    so an entity mention can (theoretically) cross a sentence
    boundary.

    The flag allow_prefix_errors indicates whether we allow
    inconsistent BIO label prefixes (i.e. a B that follows an O if
    encoding is BIO-1 or an I that follows an O if encoding is
    BIO-2). If True, we ignore the inconsistency and consider that the
    token if the first token of a mention. If False, we raise an error
    and stop.

    The flag allow_type_errors indicates whether we allow inconsistent
    label entity types, i.e. a B that follows a B or I with a
    different entity type if encoding is BIO-1, or an I that follows a
    B or I with a different entity type if encoding is BIO-2. If
    False, we raise an error and stop. If True, we ignore the error.
    In this case, if encoding is BIO-2, we consider that the prefix
    has precedence over the entity type, so we include the token in
    the same mention as the previous token (note that we don't correct
    the entity types, so they will not match); if we gave precedence
    to the entity type, we could consider that the prefix is wrong and
    act as if it were a B. In the encoding is BIO-1, there is less
    ambiguity as to the nature of the error: the different entity
    types indicate that there are 2 different mentions, as does the
    second (B) prefix, so we can be confident that the B should be an
    I (otherwise both the prefix and entity type are wrong).

    """

    if encoding not in ["BIO-1", "BIO-2"]:
        raise ValueError("unrecognized label encoding '{}'".format(label_encoding))

    # Load data, create list of sentences. A sentence is a list of
    # (line offset, token, label) tuples. If ignore_boundaries=True,
    # then we just make one long sentence.
    with open(path) as f:
        sents = []
        current_sent = []
        line_count = 0
        for line in f:
            elems = line.strip().split()
            if len(elems):
                token = elems[0]
                label = elems[label_col]
                current_sent.append((line_count, token, label))
            elif not ignore_boundaries:
                if len(current_sent):
                    sents.append(current_sent[:])
                current_sent = []
            line_count += 1
        if len(current_sent):
            sents.append(current_sent[:])

    # Get entity mentions
    mentions = []
    for sent in sents:
        if encoding == "BIO-1":
            mentions += _get_mentions_bio1(sent, allow_prefix_errors, allow_type_errors)
        elif encoding == "BIO-2":
            mentions += _get_mentions_bio2(sent, allow_prefix_errors, allow_type_errors)
    return mentions


def _get_mentions_bio1(sent, allow_prefix_errors, allow_type_errors):
    """
    Extract entity mentions from sentence (BIO-1 encoding).

    Input:

    - sent: list of (line offset, token, label) tuples

    - allow_prefix_errors: flag that indicates whether we allow a B to
      follow an O. If True, we consider that this token if the first
      token of a mention. If False, we raise an error and stop.

    - allow_type_errors: flag that specifies whether we allow a B to
      follow a B or I that has a different entity type. If False, we
      raise an error and stop. If True, we ignore the error and
      consider that the token is indeed the first token of a
      mention. There is little ambiguity as to the nature of the
      error: the different entity types indicate that there are 2
      different mentions, as does the second (B) prefix, so we can be
      confident that the B should be an I (otherwise both the prefix
      and entity type are wrong).

    Output:

    - list containing a (line offset, tokens, labels) tuple for each mention

    """
    mentions = []
    mention_tokens = []
    mention_labels = []
    prev_prefix = "O"
    prev_etype = None
    # Add an O to the end of the sentence to catch sentence-ending mentions
    padded_sent = sent[:]
    padded_sent.append((padded_sent[-1][0]+1, None, "O"))
    for (line, token, label) in padded_sent:
        # Split label into BIO prefix and entity type
        prefix = label[0]
        if prefix != "O":
            etype = label[2:]
        else:
            etype = None

        # Check for labeling inconsistencies. A B should follow a B or
        # I of the same entity type.
        if prefix == "B":
            # Check previous prefix.
            if prev_prefix == "O":
                if allow_prefix_errors:
                    # Although this B prefix is inconsistent, we
                    # ignore the error (see function documentation).
                    pass
                else:
                    msg = "ERROR at line {}: B found after an O".format(line)
                    raise ValueError(msg)
            # Check previous entity type.
            if etype != prev_etype:
                if allow_type_errors:
                    # Although this entity type is inconsistent, we
                    # ignore the error (see function documentation).
                    pass
                else:
                    msg = "ERROR at line {}: ".format(line)
                    msg += "B-{} found after {}-{}".format(etype, prev_prefix, prev_etype)
                    raise ValueError(msg)

        # Check if a mention starts here. Note that if this is a B
        # and it follows an O, we still consider that a mention starts
        # here, unless allow_prefix_errors is False, in which case an
        # error will already have been raised. See function
        # documentation for more details.
        mention_starts_here = False
        if (prefix == "I" and etype != prev_etype) or prefix == "B":
            mention_starts_here = True

        # Check if the previous token was the last token of a
        # mention. If so, output that mention, and initialize a new mention.
        if prev_etype and (prefix=="O" or mention_starts_here):
            line_offset = line-len(mention_tokens)
            mentions.append((line_offset, mention_tokens, mention_labels))
            mention_tokens = []
            mention_labels = []

        # If token is part of a mention, append token and label to
        # those of the current mention. Note that if the label entity
        # type is not consistent with those of the other tokens in the
        # mention, we ignore this error, unless allow_type_errors is
        # False, in which case an error will already have been
        # raised. See function documentation for more details.
        if prefix != "O":
            mention_tokens.append(token)
            mention_labels.append(label)

        # Prepare to move on to next token
        prev_prefix = prefix
        prev_etype = etype
    return mentions

def _get_mentions_bio2(sent, allow_prefix_errors, allow_type_errors):
    """Extract entity mentions from sentence (BIO-2 encoding).

    Input:

    - sent: list of (line offset, token, label) tuples

    - allow_prefix_errors: flag that indicates whether we allow an I
      to follow an O. If True, we consider that this token if the
      first token of a mention (note that we do not correct the
      prefixes). If False, we raise an error and stop.

    - allow_type_errors: flag that specifies whether we allow an I to
      follow an I or B that has a different entity type. If False, we
      raise an error and stop. If True, we ignore the error. In this
      case, we consider that that the prefix has precedence over the
      entity type, and include the token in the same mention as the
      previous token (note that we do not correct the entity types, so
      they will not match); if we gave precedence to the entity type,
      we could consider that the prefix is wrong and act as if it were
      a B.

    Output:

    - list containing a (line offset, tokens, labels) tuple for each mention

    """
    mentions = []
    mention_tokens = []
    mention_labels = []
    prev_prefix = "O"
    prev_etype = None
    # Add an O to the end of the sentence to catch sentence-ending mentions
    padded_sent = sent[:]
    padded_sent.append((padded_sent[-1][0]+1, None, "O"))
    for (line, token, label) in padded_sent:
        # Split label into BIO prefix and entity type
        prefix = label[0]
        if prefix != "O":
            etype = label[2:]
        else:
            etype = None

        # Check for labeling inconsistencies. An I should follow a B or
        # I of the same entity type.
        if prefix == "I":
            # Check previous prefix.
            if prev_prefix == "O":
                if allow_prefix_errors:
                    # Although this I prefix is inconsistent, we
                    # ignore the error (see function documentation).
                    pass
                else:
                    msg = "ERROR at line {}: I found after an O".format(line)
                    raise ValueError(msg)
            # Check previous entity type.
            if etype != prev_etype:
                if allow_type_errors:
                    # Although this entity type is inconsistent, we
                    # ignore the error (see function documentation).
                    pass
                else:
                    msg = "ERROR at line {}: ".format(line)
                    msg += "I-{} found after {}-{}".format(etype, prev_prefix, prev_etype)
                    raise ValueError(msg)

        # Check if a mention starts here. Note that if this is an I
        # and it follows an O, we still consider that a mention starts
        # here, unless allow_prefix_errors is False, in which case an
        # error will already have been raised. See function
        # documentation for more details.
        mention_starts_here = False
        if prefix == "B" or (prefix == "I" and prev_prefix == "O"):
            mention_starts_here = True

        # Check if the previous token was the last token of a
        # mention. If so, output that mention, and initialize a new mention.
        if prev_etype and (prefix=="O" or mention_starts_here):
            line_offset = line-len(mention_tokens)
            mentions.append((line_offset, mention_tokens, mention_labels))
            mention_tokens = []
            mention_labels = []

        # If token is part of a mention, append token and label to
        # those of the current mention. Note that if the label entity
        # type is not consistent with those of the other tokens in the
        # mention, we ignore this error, unless allow_type_errors is
        # False, in which case an error will already have been
        # raised. See function documentation for more details.
        if prefix != "O":
            mention_tokens.append(token)
            mention_labels.append(label)

        # Prepare to move on to next token
        prev_prefix = prefix
        prev_etype = etype
    return mentions

