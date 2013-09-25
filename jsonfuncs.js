function remove_comments(data) {
    data = data.toString();

    // Remove full line comments, including the newline.
    comments = new RegExp('[ \t]*//.*\r?\n', 'g');
    data = data.replace(comments, '');
    delete comments

    // Remove all remaining (in line) comments
    comments = new RegExp('//.*$', 'gm');
    data = data.replace(comments, '');
    delete comments;

    return data;
}
module.exports.remove_comments = remove_comments;
