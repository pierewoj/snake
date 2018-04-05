deploy_bundle_name="lambda_bundle.zip"
build_dir="build"
rm -rf ${build_dir}
mkdir ${build_dir}
pip install -r requirements.txt -t ${build_dir}
cp -r src/* ${build_dir}
python ${build_dir}/lambda_function.py # this just checks syntax / modules
rm ${deploy_bundle_name}
cd ${build_dir} ; zip -q -r ../${deploy_bundle_name} *