-- Insert sample patient data for testing purposes
-- $ mysql -u openemr -p openemr < sql/insert_f4patients.sql

INSERT INTO `patient_data` (
    `title`, `language`, `financial`, `fname`, `lname`, `mname`, `DOB`, 
    `street`, `postal_code`, `city`, `state`, `country_code`, 
    `drivers_license`, `ss`, `occupation`, `phone_home`, `phone_biz`, 
    `phone_cell`, `status`, `sex`, `email`, `race`, `ethnicity`, 
    `pubpid`, `hipaa_mail`, `hipaa_voice`, `regdate`
) VALUES (
    'Mr.', 'english', '1', 'Reed', 'Richards', 'Nathaniel', '1980-04-15',
    '42 Fantastic Four Blvd', '10001', 'New York', 'NY', 'US',
    'NY12345678', '123-45-6789', 'Scientist/Adventurer', '212-555-1961', '212-555-1962',
    '212-555-1963', 'active', 'Male', 'reed.richards@fantasticfour.org', 'White', 'Not Hispanic or Latino',
    'FF001', 'YES', 'YES', NOW()
);

INSERT INTO `patient_data` (
    `pid`, `title`, `language`, `financial`, `fname`, `lname`, `mname`, `DOB`, 
    `street`, `postal_code`, `city`, `state`, `country_code`, 
    `drivers_license`, `ss`, `occupation`, `phone_home`, `phone_biz`, 
    `phone_cell`, `status`, `sex`, `email`, `race`, `ethnicity`, 
    `pubpid`, `hipaa_mail`, `hipaa_voice`, `regdate`
) VALUES (
    1002, 'Mrs.', 'english', '1', 'Susan', 'Richards', 'Storm', '1982-07-15',
    '42 Fantastic Four Blvd', '10001', 'New York', 'NY', 'US',
    'NY87654321', '987-65-4321', 'Scientist/Adventurer', '212-555-1961', '212-555-1964',
    '212-555-1965', 'active', 'Female', 'sue.richards@fantasticfour.org', 'White', 'Not Hispanic or Latino',
    'FF002', 'YES', 'YES', NOW()
);

INSERT INTO `patient_data` (
    `pid`, `title`, `language`, `financial`, `fname`, `lname`, `mname`, `DOB`, 
    `street`, `postal_code`, `city`, `state`, `country_code`, 
    `drivers_license`, `ss`, `occupation`, `phone_home`, `phone_biz`, 
    `phone_cell`, `status`, `sex`, `email`, `race`, `ethnicity`, 
    `pubpid`, `hipaa_mail`, `hipaa_voice`, `regdate`
) VALUES (
    1003, 'Mr.', 'english', '1', 'Benjamin', 'Grimm', 'Jacob', '1978-11-09',
    '42 Fantastic Four Blvd', '10001', 'New York', 'NY', 'US',
    'NY12345678', '123-45-6789', 'Pilot/Adventurer', '212-555-1961', '212-555-1964',
    '212-555-1966', 'active', 'Male', 'ben.grimm@fantasticfour.org', 'White', 'Not Hispanic or Latino',
    'FF003', 'YES', 'YES', NOW()
);

INSERT INTO `patient_data` (
    `pid`, `title`, `language`, `financial`, `fname`, `lname`, `mname`, `DOB`, 
    `street`, `postal_code`, `city`, `state`, `country_code`, 
    `drivers_license`, `ss`, `occupation`, `phone_home`, `phone_biz`, 
    `phone_cell`, `status`, `sex`, `email`, `race`, `ethnicity`, 
    `pubpid`, `hipaa_mail`, `hipaa_voice`, `regdate`
) VALUES (
    1004, 'Mr.', 'english', '1', 'Jonathan', 'Storm', 'Lowell', '1985-04-20',
    '42 Fantastic Four Blvd', '10001', 'New York', 'NY', 'US',
    'NY98765432', '456-78-9123', 'Adventurer/Racer', '212-555-1961', '212-555-1964',
    '212-555-1967', 'active', 'Male', 'johnny.storm@fantasticfour.org', 'White', 'Not Hispanic or Latino',
    'FF004', 'YES', 'YES', NOW()
);
