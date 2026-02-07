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
-- Sample Data (Optional - for testing)
-- ============================================================================

-- Insert sample books
INSERT INTO books (title, author, isbn, published_year, genre, total_copies, available_copies) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 1925, 'Classic Fiction', 3, 3),
('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 1960, 'Classic Fiction', 2, 2),
('1984', 'George Orwell', '9780451524935', 1949, 'Dystopian Fiction', 4, 4),
('Pride and Prejudice', 'Jane Austen', '9780141439518', 1813, 'Romance', 2, 2),
('The Catcher in the Rye', 'J.D. Salinger', '9780316769488', 1951, 'Coming-of-age', 3, 3),

('The Hobbit', 'J.R.R. Tolkien', '9780547928227', 1937, 'Fantasy', 5, 5),
('Harry Potter and the Sorcerer''s Stone', 'J.K. Rowling', '9780590353427', 1997, 'Fantasy', 6, 6),
('Harry Potter and the Chamber of Secrets', 'J.K. Rowling', '9780439064873', 1998, 'Fantasy', 5, 5),
('The Lord of the Rings', 'J.R.R. Tolkien', '9780618640157', 1954, 'Fantasy', 4, 4),
('The Alchemist', 'Paulo Coelho', '9780061122415', 1988, 'Philosophical Fiction', 5, 5),

('The Kite Runner', 'Khaled Hosseini', '9781594631931', 2003, 'Drama', 4, 4),
('A Thousand Splendid Suns', 'Khaled Hosseini', '9781594483851', 2007, 'Drama', 3, 3),
('Life of Pi', 'Yann Martel', '9780156027328', 2001, 'Adventure', 4, 4),
('The Book Thief', 'Markus Zusak', '9780375842207', 2005, 'Historical Fiction', 3, 3),
('The Da Vinci Code', 'Dan Brown', '9780307474278', 2003, 'Thriller', 5, 5),

('Angels and Demons', 'Dan Brown', '9780743493468', 2000, 'Thriller', 4, 4),
('Inferno', 'Dan Brown', '9780385537858', 2013, 'Thriller', 3, 3),
('The Girl with the Dragon Tattoo', 'Stieg Larsson', '9780307454546', 2005, 'Crime Fiction', 3, 3),
('Gone Girl', 'Gillian Flynn', '9780307588371', 2012, 'Psychological Thriller', 4, 4),
('The Shining', 'Stephen King', '9780307743657', 1977, 'Horror', 3, 3),

('It', 'Stephen King', '9781501142970', 1986, 'Horror', 4, 4),
('The Road', 'Cormac McCarthy', '9780307387899', 2006, 'Post-apocalyptic', 2, 2),
('Dune', 'Frank Herbert', '9780441013593', 1965, 'Science Fiction', 5, 5),
('Foundation', 'Isaac Asimov', '9780553293357', 1951, 'Science Fiction', 4, 4),
('Brave New World', 'Aldous Huxley', '9780060850524', 1932, 'Dystopian Fiction', 3, 3),

('Sapiens', 'Yuval Noah Harari', '9780062316097', 2011, 'Non-fiction', 4, 4),
('Homo Deus', 'Yuval Noah Harari', '9780062464316', 2015, 'Non-fiction', 3, 3),
('Atomic Habits', 'James Clear', '9780735211292', 2018, 'Self-help', 5, 5),
('Deep Work', 'Cal Newport', '9781455586691', 2016, 'Self-help', 3, 3),
('Thinking, Fast and Slow', 'Daniel Kahneman', '9780374533557', 2011, 'Psychology', 4, 4),

('The White Tiger', 'Aravind Adiga', '9781416562597', 2008, 'Indian Fiction', 3, 3),
('Midnight''s Children', 'Salman Rushdie', '9780812976533', 1981, 'Indian Fiction', 2, 2),
('The God of Small Things', 'Arundhati Roy', '9780679457312', 1997, 'Indian Fiction', 3, 3),
('The Palace of Illusions', 'Chitra Banerjee Divakaruni', '9780385721424', 2008, 'Mythological Fiction', 3, 3),
('Train to Pakistan', 'Khushwant Singh', '9780143065883', 1956, 'Historical Fiction', 2, 2),

('Ikigai', 'Hector Garcia', '9780143130727', 2016, 'Self-help', 4, 4),
('Rich Dad Poor Dad', 'Robert Kiyosaki', '9781612680194', 1997, 'Personal Finance', 5, 5),
('The Psychology of Money', 'Morgan Housel', '9780857197689', 2020, 'Finance', 4, 4),
('The Subtle Art of Not Giving a F*ck', 'Mark Manson', '9780062457714', 2016, 'Self-help', 3, 3),
('Man''s Search for Meaning', 'Viktor Frankl', '9780807014271', 1946, 'Philosophy', 3, 3)

ON CONFLICT (isbn) DO NOTHING;

-- Insert sample members
INSERT INTO members (name, email, phone, address) VALUES

('Rahul Sharma', 'rahul.sharma@gmail.com', '9876543210', 'Baner Road, Pune'),
('Priya Verma', 'priya.verma@yahoo.in', '9123456781', 'Aundh, Pune'),
('Amit Kulkarni', 'amit.kulkarni@gmail.com', '9823012345', 'Kothrud, Pune'),
('Sneha Patil', 'sneha.patil@gmail.com', '9765432109', 'Wakad, Pune'),
('Rohit Deshmukh', 'rohit.deshmukh@outlook.com', '9898989898', 'Hinjewadi Phase 1, Pune'),
('Neha Joshi', 'neha.joshi@gmail.com', '9001122334', 'Karve Nagar, Pune'),
('Sanket Pawar', 'sanket.pawar@yahoo.in', '9012345678', 'Hadapsar, Pune'),
('Pooja Chavan', 'pooja.chavan@gmail.com', '9988776655', 'Viman Nagar, Pune'),
('Ankit Mishra', 'ankit.mishra@gmail.com', '9876501234', 'Magarpatta, Pune'),
('Kavita More', 'kavita.more@rediffmail.com', '9867543210', 'Sinhagad Road, Pune'),
('Nilesh Bhosale', 'nilesh.bhosale@gmail.com', '9811122233', 'Pashan, Pune'),
('Rutuja Jadhav', 'rutuja.jadhav@yahoo.in', '9765001122', 'Bibwewadi, Pune'),
('Swapnil Shinde', 'swapnil.shinde@gmail.com', '9822445566', 'Nigdi, Pune'),
('Manisha Kulkarni', 'manisha.k@gmail.com', '9009988776', 'Balewadi, Pune'),
('Pratik Gokhale', 'pratik.gokhale@outlook.com', '8899776655', 'Deccan Gymkhana, Pune'),

('Arjun Reddy', 'arjun.reddy@gmail.com', '9886012345', 'Whitefield, Bangalore'),
('Ananya Iyer', 'ananya.iyer@gmail.com', '9900123456', 'Indiranagar, Bangalore'),
('Karthik Rao', 'karthik.rao@yahoo.com', '9845098765', 'JP Nagar, Bangalore'),
('Sumanth Shetty', 'sumanth.shetty@gmail.com', '9988001122', 'Yelahanka, Bangalore'),
('Divya Nair', 'divya.nair@outlook.com', '9734567890', 'HSR Layout, Bangalore'),
('Vivek Agarwal', 'vivek.agarwal@gmail.com', '9823344556', 'BTM Layout, Bangalore'),
('Megha Kulkarni', 'megha.k@gmail.com', '9000012345', 'Electronic City, Bangalore'),
('Rakesh Singh', 'rakesh.singh@gmail.com', '9871122334', 'Marathahalli, Bangalore'),
('Shilpa Das', 'shilpa.das@yahoo.in', '9123012345', 'Bellandur, Bangalore'),
('Naveen Kumar', 'naveen.kumar@gmail.com', '9900990099', 'Rajajinagar, Bangalore'),
('Pavan Gowda', 'pavan.gowda@gmail.com', '9740011223', 'Mysore Road, Bangalore'),
('Keerthi S', 'keerthi.s@gmail.com', '9887766554', 'Basavanagudi, Bangalore'),
('Siddharth Jain', 'siddharth.jain@gmail.com', '9812345670', 'Hebbal, Bangalore'),
('Aishwarya Rao', 'aishwarya.rao@yahoo.com', '9001234567', 'Malleshwaram, Bangalore'),
('Varun Malhotra', 'varun.malhotra@outlook.com', '9890123456', 'Sarjapur Road, Bangalore'),

('Sai Kiran', 'sai.kiran@gmail.com', '9959012345', 'Madhapur, Hyderabad'),
('Pooja Reddy', 'pooja.reddy@yahoo.com', '9848123456', 'Gachibowli, Hyderabad'),
('Harsha Vardhan', 'harsha.v@gmail.com', '9000789456', 'Kondapur, Hyderabad'),
('Anil Kumar', 'anil.kumar@gmail.com', '9985123456', 'Kukatpally, Hyderabad'),
('Swathi Rao', 'swathi.rao@outlook.com', '9866123456', 'Manikonda, Hyderabad'),
('Ravi Teja', 'raviteja@gmail.com', '9701234567', 'Miyapur, Hyderabad'),
('Deepika Choudhary', 'deepika.c@gmail.com', '9876509876', 'Hitech City, Hyderabad'),
('Vamsi Krishna', 'vamsi.krishna@yahoo.in', '9912345678', 'LB Nagar, Hyderabad'),
('Suresh Babu', 'suresh.babu@gmail.com', '9849001122', 'Ameerpet, Hyderabad'),
('Nikhil Mehta', 'nikhil.mehta@gmail.com', '9823011111', 'Begumpet, Hyderabad')

ON CONFLICT (email) DO NOTHING;
