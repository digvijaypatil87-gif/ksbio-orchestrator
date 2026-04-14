DELETE FROM `__Auth` WHERE doctype='User' AND name='Administrator' AND fieldname='password';
INSERT INTO `__Auth` (doctype, name, fieldname, password, encrypted) VALUES ('User', 'Administrator', 'password', '$pbkdf2-sha256$29000$DGGMMeZ8j7EWovT./1/L.Q$73rZBAWBQPBMxzNopAxmr3J6VKYFWkkM9n.VQM0pn3Y', 0);
