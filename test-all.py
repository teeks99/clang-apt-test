import subprocess
import string
import sys

dev_version = "10"
versions=["8", "9", "10"]
configs=[
    ("ubuntu","xenial"),
    ("ubuntu","bionic"),
    ("ubuntu","cosmic"),
    ("ubuntu","disco"),
    ("debian","stretch"),
    ("debian","buster"),
    ("debian","sid"),
    ]
debian_baseline="sid"

tag="teeks99/clang-apt-test"

apt_base = "http://apt.llvm.org/"

def make_dockerfile(version, distro, release):
    tmpl = ""
    with open("Dockerfile.template", "r") as f:
        tmpl = f.read()

    uri_dir = release
    apt_dist = "llvm-toolchain"
    if release == debian_baseline:
        uri_dir = "unstable"
    else:
        apt_dist += "-" + release
    
    if not version == dev_version:
        apt_dist += "-" + version

    matches = {
        "distro": distro,
        "release": release,
        "llvmver": version,
        "apt_uri": apt_base + uri_dir + "/",
        "apt_dist": apt_dist
    }

    s = string.Template(tmpl)
    out = s.substitute(matches)

    with open("Dockerfile", "w") as f:
        f.write(out)

def make_config(version, distro, release):
    name = "{}-{}".format(release, version)
    print("=" * 79)
    print("Starting: " + name + "\n")

    try:

        make_dockerfile(version, distro, release)

        cmd = "docker build -t {tag}:{release}-{version} ."
        cmd = cmd.format(tag=tag, release=release, version=version)
        print(cmd)
        subprocess.check_call(cmd, shell=True)
    except Exception as e:
        return "Build Failed: {}---{}".format(name, e)

    try:
        cmd = "docker run --rm -i -t {tag}:{release}-{version}"
        cmd += " clang++-{version} --version"
        cmd = cmd.format(tag=tag, release=release, version=version)
        print(cmd)
        ver_str = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT).decode()

        if not ver_str.startswith("clang version {}".format(version)):
            return "Incorrect version: {}---{}".format(name, ver_str)

    except Exception as e:
        return "Run Failed: {}---{}".format(name, e)

    return ""

def all():
    errors = []
    for version in versions:
        for config in configs:
            distro = config[0]
            release = config[1]

            error = make_config(version, distro, release)
            if error:
                print(error)
                errors.append(error)

    print("Errors encountered")
    for error in errors:
        print(error)

if __name__ == "__main__":
    if len(sys.argv) == 4:
        distro = sys.argv[1]
        release = sys.argv[2]
        version = sys.argv[3]
        print(make_config(version, distro, release))
    else:
        all()