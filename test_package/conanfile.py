from conans import ConanFile, CMake
import os

class AwssdkcppTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            # NOTE: These settings must match what's in the top-level conanfile (which is currently fixed to MD)
            if self.settings.build_type == "Release":
                self.settings.compiler.runtime = "MD"
            else:
                self.settings.compiler.runtime = "MDd"
        self.options["aws-sdk-cpp"].shared = False
        self.options["aws-sdk-cpp"].build_s3 = True
        self.options["aws-sdk-cpp"].build_logs = True
        self.options["aws-sdk-cpp"].build_monitoring = True
        self.options["aws-sdk-cpp"].build_transfer = True

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is in "test_package".
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy('*.so*', dst='bin', src='lib')

    def test(self):
        os.chdir("bin")
        self.run(".%sexample" % os.sep)
