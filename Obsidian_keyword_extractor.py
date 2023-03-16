from pathlib import Path

from rake_nltk import Rake
import os
import shutil
import click


def find_keywords(text):
    """
    extract keywords from text using rake_nltk
    :param text:  input text as a variable
    :return: top 20 keywords as a list
    """
    rake = Rake()
    rake.extract_keywords_from_text(text)
    keywords = set(rake.get_ranked_phrases_with_scores())  # set to keep only unique

    # extract top20 single keywords by rating
    keyword_result = {}  # create dict to store the results
    for rating, keyword in keywords:
        if (len(keyword.split()) == 1) and (
                keyword.isalpha()):  # if single keyword and if the word is only alphabetical (remove numbers)
            keyword_result[keyword] = rating  # convert to dict to rank keywords by score
        # sort dictionary by score
    keyword_sorted = dict(sorted(keyword_result.items(), key=lambda x: x[1], reverse=True))
    # get only the first 20 entries
    return list(keyword_sorted)[0:20]


def backup_file(filename, source, dest, confirmation=True):
    """
    copy original note files to create a backup
    :param filename: filename of the original notes including extension
    :param source: path of source file
    :param dest: path of dest file
    :param confirmation: print a confirmation for each file copied (default True
    :return: copy files and print confirmation
    """
    shutil.copyfile(source, dest)
    if confirmation:  # if True
        print(filename + " => copied successfully from " + source + " to " + dest)
    else:
        pass


# create function to copy tag_block to the file, at the beginning
def add_tag_block_to_file(filename, keyword_list, config_path):
    """
    create a tag block containing the top keywords as hashtags at the beginning of the note
    :param config_path: folder path with the notes
    :param filename: note to write on
    :param keyword_list: list of top keywords
    :return: copy note files to "output" folder and add tag block (top keywords) at the top
    """

    # copy the original file to the folder "output" to do the modification on the new file
    #                 source =   # config_path + "\\" + filename  # path of the file
    #                   dest = # config_path + "\\output\\" + filename  # path of the backup
    backup_file(filename,
                source=os.path.join(config_path, filename),
                dest=os.path.join(config_path, "output", filename),
                confirmation=False)

    # create tag block as string
    tag_block = "=====================AUTO-TAG BLOCK===================== \n"
    for keyword in keyword_list:  # add each keyword to the string
        tag_block = tag_block + "#" + keyword + " "
    tag_block = tag_block + "\n==========================================\n\n"

    # add tag_block to the beginning of the file
    note_path = os.path.join(config_path, "output", filename)
    with open(note_path, "r+", encoding="utf8") as file:
        lines = file.readlines()  # create a list containing each line followed by line break
        lines.insert(0, tag_block)  # insert the line at the beginning of the text file
        file.seek(0)  # file pointer locates at the beginning to write the whole file again
        file.writelines(lines)  # rewrite previous text after the new line
    linebreak = "-----------------------------------------"
    print(filename + " => tag block successfully added" + "\n" + linebreak)


# Main function + arguments coming from click
@click.command()
@click.argument("config_path", type=click.Path(exists=True, path_type=Path))
def main(config_path: Path):
    """
    run main function using path from click.
    https://click.palletsprojects.com/en/8.1.x/arguments/#file-path-arguments
    :param config_path: path of the folder containing the notes
    :return: apply all the functions of this project
    """

    # Create list of paths of note files in the folder with the notes
    list_file = []
    for path in os.listdir(config_path):  # iterate on directory
        # check if current path is file or folder
        if os.path.isfile(os.path.join(config_path, path)):
            list_file.append(path)  # add to the result list

    # loop to apply functions and iterate over files
    for filename in list_file:
        # copy text from the file to a variable named "text"
        file_path = os.path.join(config_path, filename)
        with open(file_path, "r+", encoding="utf8") as file:  # "with open" automatically close the file!
            text = file.read()

        # apply function "find keyword" to the text
        keyword_list = find_keywords(text)

        # apply function "backup file"
        backup_file(filename=filename,
                    source=os.path.join(config_path, filename),
                    dest=os.path.join(config_path, "backup", filename))

        # apply function "add tag to file"
        add_tag_block_to_file(filename, keyword_list, config_path)


if __name__ == "__main__":
    main()
