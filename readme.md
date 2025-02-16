# API Tests Project

This project executes API tests on the following endpoints:
1. **Barrels**
2. **Measurements**

The apitest framework is using **pytest**
also supports generating test documentation using **Sphinx** and **Allure Reports**.
is also possible to switch test in runtime and test will run according --host
parameter.


    1. run all tests
    pytest -s -v --host=prod

    2. run all tests with allure and generate report
        pytest -s -v --host=prod --alluredir="./allure_dir" 
        allure serve ./allure_dir 
    
    3. generate test documentation for api test with 
    ./generate_doc.bat









