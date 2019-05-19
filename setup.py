from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from xml.dom.minidom import parse
import configparser
import shutil
import os


this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        # TODO
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        path = shutil.which('woeusbgui')  # I have no clue how to find were pip puts exec's
        if path is None:
            path = 'usr/local/bin/woeusbgui'
        else:
            dom = parse(this_directory + '/miscellaneous/com.github.woeusb.woeusb-ng.policy')
            for action in dom.getElementsByTagName('action'):
                if action.getAttribute('id') == "com.github.slacka.woeusb.run-gui-using-pkexec":
                    for annotate in action.getElementsByTagName('annotate'):
                        if annotate.getAttribute('key') == "org.freedesktop.policykit.exec.path":
                            annotate.childNodes[0].nodeValue = path

            with open(this_directory + '/miscellaneous/com.github.woeusb.woeusb-ng.policy', "w") as file:
                dom.writexml(file)

        shutil.copy2(this_directory + '/miscellaneous/com.github.woeusb.woeusb-ng.policy', "/usr/share/polkit-1/actions")

        try:
            os.makedirs('/usr/share/icons/WoeUSB-ng')
        except FileExistsError:
            pass

        shutil.copy2(this_directory + '/WoeUSB/data/icon.ico', '/usr/share/icons/WoeUSB-ng/icon.ico')

        desktop = configparser.ConfigParser()
        desktop.read(this_directory + '/miscellaneous/WoeUSB-ng.desktop')
        desktop.set('Desktop Entry', 'value', path)
        with open(this_directory + '/miscellaneous/WoeUSB-ng.desktop', "w") as file:
            desktop.write(file)

        shutil.copy2(
            this_directory + '/miscellaneous/WoeUSB-ng.desktop',
            '/home/' + os.environ['SUDO_USER'] + '/.local/share/applications'
        )

        install.run(self)


setup(
    name='WoeUSB-ng',
    version='0.1.5',
    description='WoeUSB-ng is a simple tool that enable you to create your own usb stick windows installer from an iso image or a real DVD. It is a rewrite of original WoeUSB. ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='http://github.com/WoeUSB/WoeUSB-ng',
    author='Jakub Szymański',
    author_email='jakubmateusz@poczta.onet.pl',
    license='GPL-3',
    zip_safe=False,
    packages=['WoeUSB'],
    include_package_data=True,
    scripts=[
        'WoeUSB/woeusb',
        'WoeUSB/woeusbgui'
    ],
    install_requires=[
        'termcolor',
        'wxPython',
    ],
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand
    }
)
