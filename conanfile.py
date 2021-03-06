from conans import ConanFile, CMake, tools
import os

def merge_dicts_for_sdk(a, b):
    res = a.copy()
    res.update(b)
    return res

class AwssdkcppConan(ConanFile):
    name = "aws-sdk-cpp"
    version = "1.7.257"
    license = "Apache 2.0"
    url = "https://github.com/kmaragon/conan-aws-sdk-cpp"
    description = "Conan Package for aws-sdk-cpp"
    short_paths = True
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = "zlib/1.2.11"
    exports_sources = ["patch-cmakelists.patch", "patch-c-libs.patch"]
    sdks = ("access_management",
            "acm",
            "alexaforbusiness"
            "amplify"
            "apigateway",
            "application_autoscaling",
            "appstream",
            "appsync",
            "athena",
            "autoscaling",
            "batch",
            "budgets",
            "chime",
            "cloud9",
            "clouddirectory",
            "cloudformation",
            "cloudfront",
            "cloudhsmv2",
            "cloudsearch",
            "cloudtrail",
            "codebuild",
            "codecommit",
            "codedeploy",
            "codepipeline",
            "codestar",
            "cognito_identity",
            "cognito_idp",
            "cognito_sync",
            "comprehend",
            "config",
            "cur",
            "datapipeline",
            "dax",
            "devicefarm",
            "directconnect",
            "discovery",
            "dlm",
            "dms",
            "docdb",
            "ds",
            "dynamodb",
            "dynamodbstreams",
            "ec2",
            "ecr",
            "ecs",
            "eks",
            "elasticache",
            "elasticbeanstalk",
            "elasticfilesystem",
            "elasticloadbalancing",
            "elasticloadbalancingv2",
            "elasticmapreduce",
            "elastictranscoder",
            "email",
            "es",
            "events",
            "firehose",
            "fms",
            "fsx",
            "gamelift",
            "glacier",
            "globalaccelerator",
            "glue",
            "greengrass",
            "guardduty",
            "health",
            "iam",
            "identity_management",
            "importexport",
            "inspector",
            "iot_data",
            "iot_jobs_data",
            "iot",
            "kafka",
            "kinesis",
            "kinesisanalytics",
            "kinesisvideo",
            "kms",
            "lambda",
            "lex",
            "lightsail",
            "logs",
            "machinelearnings",
            "macie",
            "marketplace_entitlement",
            "marketplacecommerceanalytics",
            "mediaconvert",
            "medialive",
            "mediapackage",
            "mediastore",
            "mediatailor",
            "meteringmarketplace",
            "mobileanalytics",
            "monitoring",
            "mq",
            "mturk_requester",
            "neptune",
            "opsworks",
            "opsworkscm",
            "organizations",
            "pinpoint",
            "polly",
            "pricing",
            "queues",
            "quicksight",
            "ram",
            "rds",
            "redshift",
            "recognition",
            "resource_groups",
            "robomaker"
            "route53",
            "route53domains",
            "s3",
            "sagemaker",
            "sdb",
            "serverlessrepo"
            "servicecatalog",
            "servicediscovery",
            "shield",
            "signer",
            "sms",
            "snowball",
            "sns",
            "sqs",
            "ssm",
            "states",
            "storagegateway",
            "sts",
            "support",
            "swf",
            "text_to_speech",
            "texttract",
            "transcribe",
            "transfer",
            "translate",
            "waf",
            "workdocs",
            "worklink",
            "workmail",
            "workspaces",
            "xray"
           )
    options = merge_dicts_for_sdk({"build_" + x: [True, False] for x in sdks}, {
            "shared": [True, False],
            "min_size": [True, False]
        })
    default_options = ("shared=False","min_size=False") + tuple("build_" + x + "=False" for x in sdks)

    def requirements(self):
        if self.settings.os != "Windows":
            if self.settings.os != "Macos":
                self.requires("openssl/1.0.2t")
            self.requires("libcurl/7.67.0")

    def source(self):
        tools.download("https://github.com/aws/aws-sdk-cpp/archive/%s.tar.gz" % self.version, "aws-sdk-cpp.tar.gz")
        tools.unzip("aws-sdk-cpp.tar.gz")
        os.unlink("aws-sdk-cpp.tar.gz")

# These patches were used from the original fork (sdk v1.7.212), but seem unneeded for our use.
#         # patch the shipped CMakeLists.txt which builds stuff before even declaring a project
#         tools.patch(patch_file=os.path.join(self.source_folder, "patch-cmakelists.patch"))
#         # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
#         # if the packaged project doesn't have variables to set it properly
#         tools.patch(patch_file=os.path.join(self.source_folder, "patch-c-libs.patch"))

        # This ensures the aws cmake will find the requirements (zlib, curl, ssl)
        tools.replace_in_file(
            "aws-sdk-cpp-%s/CMakeLists.txt" % self.version,
            "project(\"aws-cpp-sdk-all\" VERSION \"${PROJECT_VERSION}\" LANGUAGES CXX)",
'''project(aws-cpp-sdk-all VERSION "${PROJECT_VERSION}" LANGUAGES CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
''')

    def build(self):
        cmake = CMake(self)
        build_only = list([])
        for sdk in self.sdks:
            if getattr(self.options, "build_" + sdk):
                build_only.append(sdk)

        cmake.definitions["BUILD_ONLY"] = ";".join(build_only)
        cmake.definitions["ENABLE_UNITY_BUILD"] = "ON"
        cmake.definitions["ENABLE_TESTING"] = "OFF"
        cmake.definitions["AUTORUN_UNIT_TESTS"] = "OFF"

        cmake.definitions["MINIMIZE_SIZE"] = "ON" if self.options.min_size else "OFF"
        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["FORCE_SHARED_CRT"] = "ON" # For windows, we force using MD/MDd

        cmake.configure(source_folder="%s/aws-sdk-cpp-%s" % (self.source_folder, self.version), build_folder=self.build_folder)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install(build_dir=self.build_folder)

    def package_info(self):
        libs = list([])

        for sdk in self.sdks:
            if getattr(self.options, "build_" + sdk):
                libs.append("aws-cpp-sdk-" + sdk)
        libs.extend(["aws-cpp-sdk-core", "aws-c-event-stream", "aws-c-common", "aws-checksums"])

        if self.settings.os == "Windows":
            libs.append("winhttp")
            libs.append("wininet")
            libs.append("bcrypt")
            libs.append("userenv")
            libs.append("version")
            libs.append("ws2_32")

        if self.settings.os == "Linux":
            libs.append("atomic")
            if self.settings.compiler == "clang":
                libs.append("-stdlib=libstdc++")

        self.cpp_info.libs = libs
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
