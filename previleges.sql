-- Admin has full access
GRANT ALL PRIVILEGES ON transport.* TO 'adminuser'@'localhost';

-- Operator can read, insert, update, but cannot delete vehicles or users
GRANT SELECT, INSERT, UPDATE ON transport.Vehicle TO 'operatoruser'@'localhost';
GRANT SELECT, INSERT, UPDATE ON transport.Trip TO 'operatoruser'@'localhost';
GRANT SELECT, INSERT, UPDATE ON transport.Station TO 'operatoruser'@'localhost';
GRANT SELECT, INSERT, UPDATE ON transport.Announcement TO 'operatoruser'@'localhost';

-- Passenger can only read/view and insert tickets, payments, and their own info
GRANT SELECT, INSERT ON transport.Ticket TO 'passengeruser'@'localhost';
GRANT SELECT, INSERT ON transport.Payment TO 'passengeruser'@'localhost';
GRANT SELECT ON transport.User TO 'passengeruser'@'localhost';
