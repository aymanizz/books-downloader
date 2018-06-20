import os
import string
import functools

def format_filename(name):
    valid_chars = ' _-.(){}{}'.format(string.ascii_letters, string.digits)
    return ''.join(c for c in name if c in valid_chars)

def generate_filename(basename, extension):
    filename_template = format_filename(basename) + '{}.' + extension
    filename = filename_template.format('')
    file_num = 0
    while os.path.exists(filename):
        file_num += 1
        filename = filename_template.format('_' + str(file_num))
    return filename

def format_size(size):
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024
    if size > GB:
        return '{:.2f} GB'.format(size / GB)
    elif size > MB:
        return '{:.2f} MB'.format(size / MB)
    elif size > KB:
        return '{:.2f} KB'.format(size / KB)
    else:
        return '{} B'.format(size)

def retryable(input_f, exit_f=None, on_failure=None, on_sucess=None):
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                try:
                    return func(*args, **kwargs)
                    if on_sucess is not None:
                        on_sucess()
                    break
                except:
                    if on_failure is not None:
                        on_failure()
                    while True:
                        i = input_f()
                        if i in ['y', 'Y', 'yes', 'Yes', 'YES',
                            'n', 'N', 'no', 'No', 'NO']:
                            i = i[0].lower()
                            break
                    if i == 'y':
                        continue
                    else:
                        if exit_f is not None:
                            exit_f()
                        break
        return wrapper
    return inner