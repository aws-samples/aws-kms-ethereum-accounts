#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import setuptools

CDK_VERSION = "1.90.0"

with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="aws_kms_lambda_ethereum",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "aws_kms_lambda_ethereum"},
    packages=setuptools.find_packages(where="aws_kms_lambda_ethereum"),

    install_requires=[
        "aws-cdk.core=={}".format(CDK_VERSION),
        "aws-cdk.aws-lambda=={}".format(CDK_VERSION),
        "aws-cdk.aws-kms=={}".format(CDK_VERSION),
        "aws-cdk.aws-iam=={}".format(CDK_VERSION)

    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: MIT No Attribution License (MIT-0)",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
