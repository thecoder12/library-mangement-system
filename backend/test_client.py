#!/usr/bin/env python3
"""
Sample gRPC client script to demonstrate API usage.

This script shows how to interact with the Library gRPC service.
Run this after starting the gRPC server with: python server.py
"""

import grpc
from app.generated import library_pb2, library_pb2_grpc


def run():
    """Main function demonstrating gRPC client usage."""
    
    # Connect to the gRPC server
    channel = grpc.insecure_channel('localhost:50051')
    stub = library_pb2_grpc.LibraryServiceStub(channel)
    
    print("=" * 60)
    print("Neighborhood Library - gRPC Client Demo")
    print("=" * 60)
    
    # 1. List all books
    print("\n📚 Listing all books...")
    response = stub.ListBooks(library_pb2.ListBooksRequest(page=1, page_size=10))
    print(f"Found {response.total_count} books:")
    for book in response.books:
        print(f"  - {book.title} by {book.author} "
              f"(Available: {book.available_copies}/{book.total_copies})")
    
    # 2. Create a new book
    print("\n📖 Creating a new book...")
    new_book = stub.CreateBook(library_pb2.CreateBookRequest(
        title="The Hobbit",
        author="J.R.R. Tolkien",
        isbn="978-0547928227",
        published_year=1937,
        genre="Fantasy",
        total_copies=2
    ))
    print(f"Created book: {new_book.title} (ID: {new_book.id})")
    
    # 3. List all members
    print("\n👥 Listing all members...")
    response = stub.ListMembers(library_pb2.ListMembersRequest(page=1, page_size=10))
    print(f"Found {response.total_count} members:")
    for member in response.members:
        status = "Active" if member.is_active else "Inactive"
        print(f"  - {member.name} ({member.email}) - {status}")
    
    # 4. Create a new member
    print("\n👤 Creating a new member...")
    new_member = stub.CreateMember(library_pb2.CreateMemberRequest(
        name="Alice Johnson",
        email="alice.johnson@email.com",
        phone="555-0104",
        address="321 Elm St, Springfield"
    ))
    print(f"Created member: {new_member.name} (ID: {new_member.id})")
    
    # 5. Borrow a book
    print("\n📤 Borrowing a book...")
    try:
        borrow_record = stub.BorrowBook(library_pb2.BorrowBookRequest(
            book_id=new_book.id,
            member_id=new_member.id
        ))
        print(f"Borrow record created (ID: {borrow_record.id})")
        print(f"  Book: {borrow_record.book.title}")
        print(f"  Member: {borrow_record.member.name}")
        print(f"  Due date: {borrow_record.due_date}")
    except grpc.RpcError as e:
        print(f"Error borrowing book: {e.details()}")
    
    # 6. Get member's borrowed books
    print("\n📋 Getting member's borrowed books...")
    response = stub.GetMemberBorrowedBooks(
        library_pb2.GetMemberBorrowedBooksRequest(member_id=new_member.id)
    )
    print(f"Member {response.member.name} has {len(response.records)} borrowed book(s):")
    for record in response.records:
        print(f"  - {record.book.title} (Due: {record.due_date})")
    
    # 7. Return the book
    print("\n📥 Returning the book...")
    try:
        returned = stub.ReturnBook(library_pb2.ReturnBookRequest(
            borrow_id=borrow_record.id
        ))
        print(f"Book returned successfully!")
        print(f"  Return date: {returned.return_date}")
        print(f"  Status: {returned.status}")
    except grpc.RpcError as e:
        print(f"Error returning book: {e.details()}")
    
    # 8. Verify book availability is restored
    print("\n🔍 Checking book availability...")
    book = stub.GetBook(library_pb2.GetBookRequest(id=new_book.id))
    print(f"Book '{book.title}': {book.available_copies}/{book.total_copies} available")
    
    # 9. Cleanup - delete test data
    print("\n🧹 Cleaning up test data...")
    stub.DeleteBook(library_pb2.DeleteBookRequest(id=new_book.id))
    print(f"Deleted book: {new_book.title}")
    stub.DeleteMember(library_pb2.DeleteMemberRequest(id=new_member.id))
    print(f"Deleted member: {new_member.name}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run()
