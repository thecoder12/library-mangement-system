-- Neighborhood Library Database Schema
-- PostgreSQL initialization script

-- Create extension for UUID support (optional, for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Books Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    published_year INTEGER,
    genre VARCHAR(100),
    total_copies INTEGER NOT NULL DEFAULT 1,
    available_copies INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT positive_copies CHECK (total_copies >= 0),
    CONSTRAINT available_not_exceed_total CHECK (available_copies >= 0 AND available_copies <= total_copies)
);

-- Index for searching books
CREATE INDEX IF NOT EXISTS idx_books_title ON books (title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books (author);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books (isbn);

-- ============================================================================
-- Members Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    membership_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for searching members
CREATE INDEX IF NOT EXISTS idx_members_name ON members (name);
CREATE INDEX IF NOT EXISTS idx_members_email ON members (email);

-- ============================================================================
-- Borrow Records Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS borrow_records (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
    borrow_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'BORROWED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('BORROWED', 'RETURNED')),
    CONSTRAINT valid_dates CHECK (due_date >= borrow_date)
);

-- Index for querying borrow records
CREATE INDEX IF NOT EXISTS idx_borrow_records_book_id ON borrow_records (book_id);
CREATE INDEX IF NOT EXISTS idx_borrow_records_member_id ON borrow_records (member_id);
CREATE INDEX IF NOT EXISTS idx_borrow_records_status ON borrow_records (status);

-- ============================================================================
-- Trigger function to update 'updated_at' timestamp
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables
DROP TRIGGER IF EXISTS update_books_updated_at ON books;
CREATE TRIGGER update_books_updated_at
    BEFORE UPDATE ON books
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_members_updated_at ON members;
CREATE TRIGGER update_members_updated_at
    BEFORE UPDATE ON members
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_borrow_records_updated_at ON borrow_records;
CREATE TRIGGER update_borrow_records_updated_at
    BEFORE UPDATE ON borrow_records
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Sample Data - Indian Books and Members (50 each)
-- ============================================================================

-- Insert sample books (50 Indian books)
INSERT INTO books (title, author, isbn, published_year, genre, total_copies, available_copies) VALUES
    -- Classic Indian Literature
    ('Gitanjali', 'Rabindranath Tagore', '978-8171673254', 1910, 'Poetry', 4, 4),
    ('Godan', 'Munshi Premchand', '978-8126415786', 1936, 'Literary Fiction', 3, 3),
    ('Gaban', 'Munshi Premchand', '978-8126702541', 1931, 'Literary Fiction', 2, 2),
    ('Nirmala', 'Munshi Premchand', '978-8126708521', 1927, 'Literary Fiction', 2, 2),
    ('Kabuliwala', 'Rabindranath Tagore', '978-8129116254', 1892, 'Short Stories', 3, 3),
    ('Guide', 'R.K. Narayan', '978-0143039648', 1958, 'Literary Fiction', 3, 3),
    ('Malgudi Days', 'R.K. Narayan', '978-0143031246', 1943, 'Short Stories', 4, 4),
    ('The Financial Expert', 'R.K. Narayan', '978-0226568355', 1952, 'Literary Fiction', 2, 2),
    ('Swami and Friends', 'R.K. Narayan', '978-0226568331', 1935, 'Fiction', 3, 3),
    ('Train to Pakistan', 'Khushwant Singh', '978-0143065883', 1956, 'Historical Fiction', 3, 3),
    
    -- Modern Indian Fiction
    ('The God of Small Things', 'Arundhati Roy', '978-0812979657', 1997, 'Literary Fiction', 4, 4),
    ('The White Tiger', 'Aravind Adiga', '978-1416562603', 2008, 'Literary Fiction', 3, 3),
    ('A Suitable Boy', 'Vikram Seth', '978-0060786526', 1993, 'Literary Fiction', 2, 2),
    ('Midnight Children', 'Salman Rushdie', '978-0812976533', 1981, 'Magical Realism', 3, 3),
    ('The Inheritance of Loss', 'Kiran Desai', '978-0802142818', 2006, 'Literary Fiction', 2, 2),
    ('The Namesake', 'Jhumpa Lahiri', '978-0618485222', 2003, 'Literary Fiction', 3, 3),
    ('Interpreter of Maladies', 'Jhumpa Lahiri', '978-0395927205', 1999, 'Short Stories', 4, 4),
    ('The Palace of Illusions', 'Chitra Banerjee Divakaruni', '978-0385515993', 2008, 'Mythology', 3, 3),
    ('Sea of Poppies', 'Amitav Ghosh', '978-0312428594', 2008, 'Historical Fiction', 2, 2),
    ('The Shadow Lines', 'Amitav Ghosh', '978-0618329960', 1988, 'Literary Fiction', 2, 2),
    
    -- Contemporary Popular Fiction
    ('Five Point Someone', 'Chetan Bhagat', '978-8129135476', 2004, 'Fiction', 5, 5),
    ('2 States', 'Chetan Bhagat', '978-8129115300', 2009, 'Romance', 4, 4),
    ('The 3 Mistakes of My Life', 'Chetan Bhagat', '978-8129113726', 2008, 'Fiction', 3, 3),
    ('Half Girlfriend', 'Chetan Bhagat', '978-8129136459', 2014, 'Romance', 4, 4),
    ('Revolution 2020', 'Chetan Bhagat', '978-8129118806', 2011, 'Fiction', 3, 3),
    ('The Immortals of Meluha', 'Amish Tripathi', '978-9380658742', 2010, 'Mythology', 5, 5),
    ('The Secret of the Nagas', 'Amish Tripathi', '978-9381626344', 2011, 'Mythology', 4, 4),
    ('The Oath of the Vayuputras', 'Amish Tripathi', '978-9382618348', 2013, 'Mythology', 4, 4),
    ('Scion of Ikshvaku', 'Amish Tripathi', '978-9385152146', 2015, 'Mythology', 3, 3),
    ('Sita: Warrior of Mithila', 'Amish Tripathi', '978-9386224583', 2017, 'Mythology', 3, 3),
    
    -- Indian Mythology & Spirituality
    ('The Bhagavad Gita (Translation)', 'Eknath Easwaran', '978-1586380199', 2007, 'Spirituality', 5, 5),
    ('Autobiography of a Yogi', 'Paramahansa Yogananda', '978-8120725249', 1946, 'Spirituality', 3, 3),
    ('Jaya: An Illustrated Retelling of the Mahabharata', 'Devdutt Pattanaik', '978-0143104254', 2010, 'Mythology', 4, 4),
    ('Sita: An Illustrated Retelling of the Ramayana', 'Devdutt Pattanaik', '978-0143064329', 2013, 'Mythology', 4, 4),
    ('My Gita', 'Devdutt Pattanaik', '978-8129137708', 2015, 'Spirituality', 3, 3),
    ('The Difficulty of Being Good', 'Gurcharan Das', '978-0143068570', 2009, 'Philosophy', 2, 2),
    
    -- Regional Literature (Translations)
    ('Ponniyin Selvan', 'Kalki Krishnamurthy', '978-9380034010', 1955, 'Historical Fiction', 3, 3),
    ('Parineeta', 'Sarat Chandra Chattopadhyay', '978-8129124587', 1914, 'Literary Fiction', 2, 2),
    ('Devdas', 'Sarat Chandra Chattopadhyay', '978-8129108456', 1917, 'Literary Fiction', 3, 3),
    ('Chokher Bali', 'Rabindranath Tagore', '978-0143102038', 1903, 'Literary Fiction', 2, 2),
    ('Kanneshwara Rama', 'Vikas Swarup', '978-0552773898', 2005, 'Fiction', 3, 3),
    
    -- Non-Fiction & Biographies
    ('Wings of Fire', 'A.P.J. Abdul Kalam', '978-8173711466', 1999, 'Autobiography', 5, 5),
    ('India After Gandhi', 'Ramachandra Guha', '978-0060958589', 2007, 'History', 3, 3),
    ('Discovery of India', 'Jawaharlal Nehru', '978-0143031031', 1946, 'History', 2, 2),
    ('My Experiments with Truth', 'Mahatma Gandhi', '978-0486245935', 1927, 'Autobiography', 4, 4),
    ('Ignited Minds', 'A.P.J. Abdul Kalam', '978-0143029823', 2002, 'Motivational', 3, 3),
    ('The Argumentative Indian', 'Amartya Sen', '978-0312426026', 2005, 'Essays', 2, 2),
    ('Sapiens (Hindi Translation)', 'Yuval Noah Harari', '978-9390351848', 2014, 'Non-Fiction', 4, 4),
    ('Ikigai (Hindi Translation)', 'Hector Garcia', '978-9390183524', 2016, 'Self-Help', 4, 4),
    ('Rich Dad Poor Dad (Hindi)', 'Robert Kiyosaki', '978-9389611854', 1997, 'Finance', 5, 5)
ON CONFLICT (isbn) DO NOTHING;

-- Insert sample members (52 Indian members)
INSERT INTO members (name, email, phone, address) VALUES
    
    ('Amit Sharma', 'amit.sharma@gmail.com', '9876543210', '12, Shivaji Nagar, Pune, Maharashtra'),
    ('Priya Deshmukh', 'priya.deshmukh@yahoo.com', '9876543211', '45, Koregaon Park, Pune, Maharashtra'),
    ('Rahul Patil', 'rahul.patil@outlook.com', '9876543212', '78, Bandra West, Mumbai, Maharashtra'),
    ('Sneha Kulkarni', 'sneha.kulkarni@gmail.com', '9876543213', '23, Viman Nagar, Pune, Maharashtra'),
    ('Vikram Joshi', 'vikram.joshi@hotmail.com', '9876543214', '56, Andheri East, Mumbai, Maharashtra'),
    ('Anjali Pawar', 'anjali.pawar@gmail.com', '9876543215', '89, Deccan Gymkhana, Pune, Maharashtra'),
    ('Suresh Deshpande', 'suresh.deshpande@yahoo.com', '9876543216', '34, Powai, Mumbai, Maharashtra'),
    ('Kavita Shinde', 'kavita.shinde@gmail.com', '9876543217', '67, Hadapsar, Pune, Maharashtra'),
    ('Manoj Chavan', 'manoj.chavan@outlook.com', '9876543218', '90, Thane West, Mumbai, Maharashtra'),
    ('Pooja Bhosale', 'pooja.bhosale@gmail.com', '9876543219', '12, Aundh, Pune, Maharashtra'),
    
    
    ('Rajesh Kumar', 'rajesh.kumar@gmail.com', '9876543220', '34, Indiranagar, Bengaluru, Karnataka'),
    ('Deepa Hegde', 'deepa.hegde@yahoo.com', '9876543221', '56, Koramangala, Bengaluru, Karnataka'),
    ('Arun Rao', 'arun.rao@outlook.com', '9876543222', '78, Whitefield, Bengaluru, Karnataka'),
    ('Lakshmi Shetty', 'lakshmi.shetty@gmail.com', '9876543223', '90, HSR Layout, Bengaluru, Karnataka'),
    ('Kiran Gowda', 'kiran.gowda@hotmail.com', '9876543224', '23, JP Nagar, Bengaluru, Karnataka'),
    
    
    ('Senthil Murugan', 'senthil.murugan@gmail.com', '9876543225', '45, Anna Nagar, Chennai, Tamil Nadu'),
    ('Preethi Krishnan', 'preethi.krishnan@yahoo.com', '9876543226', '67, T Nagar, Chennai, Tamil Nadu'),
    ('Ganesh Raman', 'ganesh.raman@outlook.com', '9876543227', '89, Adyar, Chennai, Tamil Nadu'),
    ('Meera Subramaniam', 'meera.subra@gmail.com', '9876543228', '12, Velachery, Chennai, Tamil Nadu'),
    ('Arjun Venkatesh', 'arjun.venkat@gmail.com', '9876543229', '34, Mylapore, Chennai, Tamil Nadu'),
    
    
    ('Rohit Verma', 'rohit.verma@gmail.com', '9876543230', '56, Dwarka Sector 12, New Delhi'),
    ('Nisha Gupta', 'nisha.gupta@yahoo.com', '9876543231', '78, Vasant Kunj, New Delhi'),
    ('Sanjay Malhotra', 'sanjay.malhotra@outlook.com', '9876543232', '90, Greater Kailash, New Delhi'),
    ('Ritu Kapoor', 'ritu.kapoor@gmail.com', '9876543233', '23, Connaught Place, New Delhi'),
    ('Vivek Khanna', 'vivek.khanna@hotmail.com', '9876543234', '45, Gurgaon Sector 56, Haryana'),
    ('Shweta Arora', 'shweta.arora@gmail.com', '9876543235', '67, Noida Sector 62, Uttar Pradesh'),
    ('Ankit Saxena', 'ankit.saxena@yahoo.com', '9876543236', '89, Rohini Sector 9, New Delhi'),
    
    
    ('Chirag Patel', 'chirag.patel@gmail.com', '9876543237', '12, CG Road, Ahmedabad, Gujarat'),
    ('Hetal Shah', 'hetal.shah@outlook.com', '9876543238', '34, Satellite, Ahmedabad, Gujarat'),
    ('Jayesh Mehta', 'jayesh.mehta@gmail.com', '9876543239', '56, Navrangpura, Ahmedabad, Gujarat'),
    ('Prachi Desai', 'prachi.desai@yahoo.com', '9876543240', '78, Vastrapur, Ahmedabad, Gujarat'),
    
    
    ('Abhishek Singh', 'abhishek.singh@gmail.com', '9876543241', '90, C-Scheme, Jaipur, Rajasthan'),
    ('Manisha Rathore', 'manisha.rathore@outlook.com', '9876543242', '23, Malviya Nagar, Jaipur, Rajasthan'),
    ('Devendra Shekhawat', 'dev.shekhawat@gmail.com', '9876543243', '45, Vaishali Nagar, Jaipur, Rajasthan'),
    
    
    ('Sourav Banerjee', 'sourav.banerjee@gmail.com', '9876543244', '67, Salt Lake, Kolkata, West Bengal'),
    ('Rituparna Chatterjee', 'rituparna.chatter@yahoo.com', '9876543245', '89, Park Street, Kolkata, West Bengal'),
    ('Arnab Mukherjee', 'arnab.mukherjee@outlook.com', '9876543246', '12, Jadavpur, Kolkata, West Bengal'),
    ('Sreelekha Das', 'sreelekha.das@gmail.com', '9876543247', '34, New Town, Kolkata, West Bengal'),
    
    
    ('Anoop Menon', 'anoop.menon@gmail.com', '9876543248', '56, Marine Drive, Kochi, Kerala'),
    ('Divya Nair', 'divya.nair@yahoo.com', '9876543249', '78, Thiruvananthapuram, Kerala'),
    ('Vineeth Pillai', 'vineeth.pillai@outlook.com', '9876543250', '90, Thrissur, Kerala'),
    
    
    ('Srinivas Reddy', 'srinivas.reddy@gmail.com', '9876543251', '23, Banjara Hills, Hyderabad, Telangana'),
    ('Padmaja Rao', 'padmaja.rao@yahoo.com', '9876543252', '45, Jubilee Hills, Hyderabad, Telangana'),
    ('Venkat Naidu', 'venkat.naidu@outlook.com', '9876543253', '67, Gachibowli, Hyderabad, Telangana'),
    ('Swathi Krishna', 'swathi.krishna@gmail.com', '9876543254', '89, Madhapur, Hyderabad, Telangana'),
    
    
    ('Gurpreet Singh', 'gurpreet.singh@gmail.com', '9876543255', '12, Model Town, Ludhiana, Punjab'),
    ('Simran Kaur', 'simran.kaur@yahoo.com', '9876543256', '34, Sector 17, Chandigarh'),
    ('Hardeep Dhillon', 'hardeep.dhillon@outlook.com', '9876543257', '56, Amritsar, Punjab'),
    
    
    ('Nikhil Jain', 'nikhil.jain@gmail.com', '9876543258', '78, Civil Lines, Lucknow, Uttar Pradesh'),
    ('Megha Agarwal', 'megha.agarwal@yahoo.com', '9876543259', '90, Gomti Nagar, Lucknow, Uttar Pradesh'),
    ('A Delete Me', 'adelete_me@yahoo.com', '9876543259', '90, Gomti Nagar, Lucknow, Uttar Pradesh'),
    ('Z Delete Me', 'zdelete_me@yahoo.com', '9876543259', '90, Gomti Nagar, Lucknow, Uttar Pradesh')
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- Sample Borrow Records (20 Borrowed + 30 Returned = 50 total)
-- ============================================================================

-- Insert RETURNED borrow records (25 records - completed transactions)
-- Note: Members 3, 8, 13, 18, 23 have no borrow history (deactivated members)
INSERT INTO borrow_records (book_id, member_id, borrow_date, due_date, return_date, status) VALUES
    -- Returned in January 2026
    (1, 1, '2025-12-15', '2025-12-29', '2025-12-28', 'RETURNED'),   -- Amit borrowed Gitanjali
    (2, 2, '2025-12-16', '2025-12-30', '2025-12-29', 'RETURNED'),   -- Priya borrowed Godan
    (11, 4, '2025-12-18', '2026-01-01', '2025-12-31', 'RETURNED'),  -- Sneha borrowed God of Small Things
    (12, 5, '2025-12-19', '2026-01-02', '2026-01-01', 'RETURNED'),  -- Vikram borrowed White Tiger
    (21, 6, '2025-12-20', '2026-01-03', '2026-01-02', 'RETURNED'),  -- Anjali borrowed Five Point Someone
    (22, 7, '2025-12-21', '2026-01-04', '2026-01-03', 'RETURNED'),  -- Suresh borrowed 2 States
    (31, 9, '2025-12-23', '2026-01-06', '2026-01-05', 'RETURNED'),  -- Manoj borrowed Bhagavad Gita
    (42, 10, '2025-12-24', '2026-01-07', '2026-01-06', 'RETURNED'), -- Pooja borrowed Wings of Fire
    
    -- Returned in early January 2026
    (5, 11, '2025-12-25', '2026-01-08', '2026-01-07', 'RETURNED'),  -- Rajesh borrowed Kabuliwala
    (6, 12, '2025-12-26', '2026-01-09', '2026-01-08', 'RETURNED'),  -- Deepa borrowed Guide
    (13, 14, '2026-01-02', '2026-01-16', '2026-01-15', 'RETURNED'), -- Lakshmi borrowed A Suitable Boy
    (14, 15, '2026-01-03', '2026-01-17', '2026-01-16', 'RETURNED'), -- Kiran borrowed Midnight Children
    (15, 16, '2026-01-04', '2026-01-18', '2026-01-17', 'RETURNED'), -- Senthil borrowed Inheritance of Loss
    (16, 17, '2026-01-05', '2026-01-19', '2026-01-18', 'RETURNED'), -- Preethi borrowed The Namesake
    (23, 19, '2026-01-07', '2026-01-21', '2026-01-20', 'RETURNED'), -- Meera borrowed 3 Mistakes of My Life
    (24, 20, '2026-01-08', '2026-01-22', '2026-01-21', 'RETURNED'), -- Arjun borrowed Half Girlfriend
    
    -- Returned mid-January 2026
    (27, 21, '2026-01-09', '2026-01-23', '2026-01-22', 'RETURNED'), -- Rohit borrowed Secret of the Nagas
    (28, 22, '2026-01-10', '2026-01-24', '2026-01-23', 'RETURNED'), -- Nisha borrowed Oath of the Vayuputras
    (34, 24, '2026-01-12', '2026-01-26', '2026-01-25', 'RETURNED'), -- Ritu borrowed Sita (Ramayana)
    (37, 25, '2026-01-13', '2026-01-27', '2026-01-26', 'RETURNED'), -- Vivek borrowed Ponniyin Selvan
    (38, 26, '2026-01-14', '2026-01-28', '2026-01-27', 'RETURNED'), -- Shweta borrowed Parineeta
    (39, 27, '2026-01-15', '2026-01-29', '2026-01-28', 'RETURNED'), -- Ankit borrowed Devdas
    (43, 28, '2026-01-16', '2026-01-30', '2026-01-29', 'RETURNED'), -- Chirag borrowed India After Gandhi
    (44, 29, '2026-01-17', '2026-01-31', '2026-01-30', 'RETURNED'), -- Hetal borrowed Discovery of India
    (45, 30, '2026-01-18', '2026-02-01', '2026-01-31', 'RETURNED'); -- Jayesh borrowed My Experiments with Truth

-- Insert BORROWED records (20 records - currently active)
INSERT INTO borrow_records (book_id, member_id, borrow_date, due_date, status) VALUES
    -- Current active borrows (borrowed in late January / early February 2026)
    (1, 31, '2026-01-20', '2026-02-03', 'BORROWED'),   -- Abhishek has Gitanjali
    (2, 32, '2026-01-21', '2026-02-04', 'BORROWED'),   -- Manisha has Godan
    (6, 33, '2026-01-22', '2026-02-05', 'BORROWED'),   -- Devendra has Guide
    (7, 34, '2026-01-23', '2026-02-06', 'BORROWED'),   -- Sourav has Malgudi Days
    (11, 35, '2026-01-24', '2026-02-07', 'BORROWED'),  -- Rituparna has God of Small Things
    (12, 36, '2026-01-25', '2026-02-08', 'BORROWED'),  -- Arnab has White Tiger
    (17, 37, '2026-01-26', '2026-02-09', 'BORROWED'),  -- Sreelekha has Interpreter of Maladies
    (21, 38, '2026-01-27', '2026-02-10', 'BORROWED'),  -- Anoop has Five Point Someone
    (22, 39, '2026-01-28', '2026-02-11', 'BORROWED'),  -- Divya has 2 States
    (26, 40, '2026-01-29', '2026-02-12', 'BORROWED'),  -- Vineeth has Immortals of Meluha
    (27, 41, '2026-01-30', '2026-02-13', 'BORROWED'),  -- Srinivas has Secret of the Nagas
    (31, 42, '2026-01-31', '2026-02-14', 'BORROWED'),  -- Padmaja has Bhagavad Gita
    (33, 43, '2026-02-01', '2026-02-15', 'BORROWED'),  -- Venkat has Jaya (Mahabharata)
    (34, 44, '2026-02-02', '2026-02-16', 'BORROWED'),  -- Swathi has Sita (Ramayana)
    (42, 45, '2026-02-03', '2026-02-17', 'BORROWED'),  -- Gurpreet has Wings of Fire
    (45, 46, '2026-02-04', '2026-02-18', 'BORROWED'),  -- Simran has My Experiments with Truth
    (46, 47, '2026-02-05', '2026-02-19', 'BORROWED'),  -- Hardeep has Ignited Minds
    (48, 48, '2026-02-06', '2026-02-20', 'BORROWED'),  -- Nikhil has Sapiens (Hindi)
    (49, 49, '2026-02-07', '2026-02-21', 'BORROWED'),  -- Megha has Ikigai (Hindi)
    (50, 50, '2026-02-08', '2026-02-22', 'BORROWED');  -- Megha also has Rich Dad Poor Dad

-- Update available_copies for books that are currently borrowed
UPDATE books SET available_copies = available_copies - 1 WHERE id = 1;   -- Gitanjali (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 2;   -- Godan (3->2)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 6;   -- Guide (3->2)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 7;   -- Malgudi Days (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 11;  -- God of Small Things (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 12;  -- White Tiger (3->2)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 17;  -- Interpreter of Maladies (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 21;  -- Five Point Someone (5->4)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 22;  -- 2 States (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 26;  -- Immortals of Meluha (5->4)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 27;  -- Secret of the Nagas (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 31;  -- Bhagavad Gita (5->4)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 33;  -- Jaya (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 34;  -- Sita (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 42;  -- Wings of Fire (5->4)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 45;  -- My Experiments with Truth (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 46;  -- Ignited Minds (3->2)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 48;  -- Sapiens Hindi (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 49;  -- Ikigai Hindi (4->3)
UPDATE books SET available_copies = available_copies - 1 WHERE id = 50;  -- Rich Dad Poor Dad Hindi (5->4)

-- ============================================================================
-- Deactivate 5 members (no borrow history)
-- ============================================================================
UPDATE members SET is_active = FALSE WHERE id = 3;   -- Rahul Joshi (Maharashtra)
UPDATE members SET is_active = FALSE WHERE id = 8;   -- Kavita Pawar (Maharashtra)
UPDATE members SET is_active = FALSE WHERE id = 13;  -- Arun Kumar (Karnataka)
UPDATE members SET is_active = FALSE WHERE id = 18;  -- Ganesh Sundaram (Tamil Nadu)
UPDATE members SET is_active = FALSE WHERE id = 23;  -- Sanjay Gupta (Delhi)
