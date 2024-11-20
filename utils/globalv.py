# Common blacklists used for experiment analysis
import ultraimport
conn = ultraimport('__dir__/../utils/sqlHelper.py').ConnDatabase('Releases')

# The libraries that can not be detected with useful version information
BAD_VERSION_RESULT_LIBS = ['react', 'vue', 'angular-loader', 'svelte']

# angular-loader: not enough version files on Cdnjs
# svelte: UI framework with no version information

FRAMEWORKS = ['react', 'vue', 'angular-loader', 'svelte', 'preact', 'next', 'vue2', 'angularjs', 'emberjs', 'angular', 'react-intl']

LIBS_WITH_UPDATE = ['flatpickr', 'js-xss', 'autotracker', 'es6-promise', 'enquire.js', 'docute', 'aframe', 'simplebar', 'qrcode', 'highlight.js', 'dayjs', 'jquery-timeago', 'sweetalert', 'tween.js', 'pubsub-js', 'cash', 'feather-icons', 'overlayscrollbars']

WEB_DATASET = ['result_100k', 'result_200k', 'result_300k', 'result_400k', 'result_500k', 'result_600k', 'result_700k', 'result_800k', 'result_900k', 'result_1M']

def releaseNumInfo():
    libs = conn.show_tables()
    release_num_dict = {}
    for libname in libs:
        release_num_dict[libname] = conn.entry_count(libname)
    return release_num_dict