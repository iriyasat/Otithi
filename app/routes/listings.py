from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Listing, Review, ListingImage, Location
from datetime import datetime
import os
import uuid

listings_bp = Blueprint('listings', __name__)

@listings_bp.route('/listing/<int:listing_id>')
def listing_redirect(listing_id):
    """Redirect singular /listing/ to plural /listings/"""
    return redirect(url_for('listings.listing_detail', listing_id=listing_id), code=301)

@listings_bp.route('/listings/<int:listing_id>')
def listing_detail(listing_id):
    """Display detailed listing information"""
    try:
        listing = Listing.get(listing_id)
        
        if not listing:
            available_listings = Listing.get_all()
            error_html = f"""
            <div style="max-width: 600px; margin: 50px auto; padding: 20px; font-family: system-ui; text-align: center;">
                <h1 style="color: #dc3545; margin-bottom: 20px;">Listing Not Found</h1>
                <p style="font-size: 18px; color: #6c757d; margin-bottom: 30px;">
                    Sorry, we couldn't find a listing with ID {listing_id}.
                </p>
                <div style="margin-top: 30px;">
                    <a href="/" style="background: #006a4e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 500;">
                        ← Back to Home
                    </a>
                </div>
            </div>
            """
            return error_html, 404
        
        # Get host information
        host = User.get(listing.host_id)
        
        # Get reviews
        reviews = Review.get_by_listing(listing_id)
        
        # Get unavailable dates
        unavailable_dates = listing.get_unavailable_dates()
        
        # Get listing images
        listing_images = ListingImage.get_by_listing(listing_id)
        
        # Calculate rating
        avg_rating = 0.0
        review_count = len(reviews)
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            avg_rating = total_rating / review_count
        
        # Prepare listing data
        listing_data = {
            'id': listing.id,
            'listing_id': listing.id,
            'title': listing.title,
            'location': listing.location,
            'address': listing.address,
            'city': listing.city,
            'country': listing.country,
            'price': listing.price,
            'price_per_night': listing.price,
            'rating': avg_rating,
            'reviews': review_count,
            'images': [img.image_filename for img in listing_images] if listing_images else ['demo_listing_1.jpg'],
            'image': listing_images[0].image_filename if listing_images else 'demo_listing_1.jpg',
            'type': listing.property_type.title(),
            'room_type': listing.property_type,
            'guests': listing.guests,
            'max_guests': listing.guests,
            'description': listing.description,
            'amenities': ','.join(listing.amenities) if listing.amenities else '',
            'latitude': listing.latitude,
            'longitude': listing.longitude,
            'host': {
                'id': host.id if host else None,
                'name': host.full_name if host else 'Unknown Host',
                'avatar': host.profile_photo if host and host.profile_photo else 'user-gear.png',
                'joined': host.joined_date.year if host else '2023',
                'verified': host.verified if host else False,
                'bio': host.bio if host else ''
            },
            'unavailable_dates': unavailable_dates
        }
        
        return render_template('host/listing_detail.html', listing=listing_data, reviews=reviews)
    
    except Exception as e:
        print(f"ERROR in listing_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading listing details: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@listings_bp.route('/listings/<int:listing_id>/review', methods=['POST'])
@login_required
def add_review(listing_id):
    """Add a review for a listing"""
    try:
        listing = Listing.get(listing_id)
        if not listing:
            flash('Listing not found.', 'error')
            return redirect(url_for('main.index'))
        
        if listing.host_id == current_user.id:
            flash('You cannot review your own listing.', 'error')
            return redirect(url_for('listings.listing_detail', listing_id=listing_id))
        
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        if not rating or not comment:
            flash('Please provide both a rating and comment.', 'error')
            return redirect(url_for('listings.listing_detail', listing_id=listing_id))
        
        try:
            rating = float(rating)
            if rating < 1 or rating > 5:
                flash('Rating must be between 1 and 5.', 'error')
                return redirect(url_for('listings.listing_detail', listing_id=listing_id))
        except ValueError:
            flash('Invalid rating value.', 'error')
            return redirect(url_for('listings.listing_detail', listing_id=listing_id))
        
        # Check if user has already reviewed
        existing_reviews = Review.get_by_listing(listing_id)
        for review in existing_reviews:
            if review.user_id == current_user.id:
                flash('You have already reviewed this listing.', 'error')
                return redirect(url_for('listings.listing_detail', listing_id=listing_id))
        
        # Create review
        review = Review.create(listing_id, current_user.id, rating, comment)
        if review:
            flash('Your review has been added successfully!', 'success')
        else:
            flash('Failed to add review. Please try again.', 'error')
        
        return redirect(url_for('listings.listing_detail', listing_id=listing_id))
    
    except Exception as e:
        flash('Error adding review.', 'error')
        return redirect(url_for('listings.listing_detail', listing_id=listing_id))

@listings_bp.route('/create_listing', methods=['GET', 'POST'])
@login_required
def create_listing():
    """Create a new listing"""
    # Add immediate debug logging
    import os
    with open('/tmp/otithi_debug.log', 'a') as f:
        f.write(f"\\n\\n=== CREATE_LISTING ROUTE CALLED ===\\n")
        f.write(f"Method: {request.method}\\n")
        f.write(f"User authenticated: {current_user.is_authenticated}\\n")
        f.write(f"User ID: {getattr(current_user, 'id', 'None')}\\n")
        f.write(f"User type: {getattr(current_user, 'user_type', 'None')}\\n")
    
    try:
        # Debug: Print request information
        print(f"CREATE LISTING DEBUG:")
        print(f"  Method: {request.method}")
        print(f"  User: {current_user.name if current_user.is_authenticated else 'Not authenticated'}")
        print(f"  User type: {getattr(current_user, 'user_type', 'No user_type')} if authenticated")
        
        with open('/tmp/otithi_debug.log', 'a') as f:
            f.write(f"Route function executing...\\n")
        
        if current_user.user_type != 'host':
            print(f"  ERROR: User is not a host (type: {getattr(current_user, 'user_type', 'None')})")
            with open('/tmp/otithi_debug.log', 'a') as f:
                f.write(f"ERROR: User is not a host (type: {getattr(current_user, 'user_type', 'None')})\\n")
            flash('Only hosts can create listings.', 'error')
            return redirect(url_for('main.dashboard'))
        
        if request.method == 'POST':
            print(f"  POST request received")
            print(f"  Form data keys: {list(request.form.keys())}")
            
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            room_type = request.form.get('room_type', '').strip()
            address = request.form.get('address', '').strip()
            city = request.form.get('city', '').strip()
            country = request.form.get('country', 'Bangladesh').strip()
            price_per_night = request.form.get('price_per_night')
            max_guests = request.form.get('max_guests')
            amenities = request.form.get('amenities', '').strip()
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            
            print(f"  Title: '{title}'")
            print(f"  Description: '{description[:50]}...' ({len(description)} chars)")
            print(f"  Room type: '{room_type}'")
            print(f"  Address: '{address}'")
            print(f"  Price: '{price_per_night}'")
            print(f"  Max guests: '{max_guests}'")
            
            # Validation
            errors = []
            
            if not title:
                errors.append('Title is required.')
            
            if not description:
                errors.append('Description is required.')
            
            if room_type not in ['entire_place', 'private_room', 'shared_room']:
                errors.append('Invalid property type selected.')
            
            if not address or not city:
                errors.append('Address and city are required.')
            
            try:
                price_per_night = float(price_per_night)
                if price_per_night <= 0:
                    errors.append('Price per night must be greater than 0.')
            except (ValueError, TypeError):
                errors.append('Please enter a valid price per night.')
            
            try:
                max_guests = int(max_guests)
                if max_guests <= 0:
                    errors.append('Maximum guests must be at least 1.')
            except (ValueError, TypeError):
                errors.append('Please enter a valid maximum guest count.')
            
            # Handle coordinates
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except (ValueError, TypeError):
                errors.append('Invalid coordinates. Please select a location on the map.')
            
            # Handle file uploads
            uploaded_files = []
            if 'listing_images' in request.files:
                files = request.files.getlist('listing_images')
                print(f"  Found {len(files)} uploaded files")
                for i, file in enumerate(files):
                    if file and file.filename:
                        print(f"    File {i+1}: {file.filename}")
                        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                        
                        if file_ext not in allowed_extensions:
                            errors.append(f'Invalid file type for image {i+1}.')
                            continue
                        
                        file.seek(0, 2)
                        file_size = file.tell()
                        file.seek(0)
                        
                        if file_size > 5 * 1024 * 1024:
                            errors.append(f'Image {i+1} is too large. Maximum size is 5MB.')
                            continue
                        
                        uploaded_files.append((file, i + 1))
            
            if not uploaded_files:
                errors.append('At least one listing image is required.')
            
            print(f"  Validation complete. Errors: {len(errors)}")
            if errors:
                print(f"  ERRORS FOUND:")
                for error in errors:
                    print(f"    - {error}")
                    flash(error, 'error')
                return render_template('host/create_listing.html')
            
            print(f"  No validation errors. Proceeding with listing creation...")
            
            # Create location
            print(f"  Creating location: {address}, {city}, {country}")
            
            # Also write to a log file for debugging
            with open('/tmp/otithi_debug.log', 'a') as f:
                f.write(f"\\n=== LISTING CREATION DEBUG {datetime.now()} ===\\n")
                f.write(f"Form data received:\\n")
                f.write(f"  Title: {title}\\n")
                f.write(f"  Description: {description[:50]}...\\n")
                f.write(f"  Room type: {room_type}\\n")
                f.write(f"  Address: {address}\\n")
                f.write(f"  City: {city}\\n")
                f.write(f"  Country: {country}\\n")
                f.write(f"  Price: {price_per_night}\\n")
                f.write(f"  Max guests: {max_guests}\\n")
                f.write(f"  Coordinates: {latitude}, {longitude}\\n")
                f.write(f"  Host ID: {current_user.id}\\n")
                f.write(f"  Files uploaded: {len(uploaded_files)}\\n")
            
            location_obj = Location.find_or_create(
                address=address,
                city=city,
                country=country,
                latitude=latitude,
                longitude=longitude
            )
            
            if not location_obj:
                print(f"  ERROR: Failed to create location")
                with open('/tmp/otithi_debug.log', 'a') as f:
                    f.write("ERROR: Failed to create location\\n")
                flash('Failed to create location. Please try again.', 'error')
                return render_template('host/create_listing.html')
            
            print(f"  Location created successfully: ID {location_obj.location_id}")
            with open('/tmp/otithi_debug.log', 'a') as f:
                f.write(f"Location created successfully: ID {location_obj.location_id}\\n")
            
            # Create listing
            print(f"  Creating listing with host_id: {current_user.id}")
            
            # Check if current_user.id is valid
            if not current_user.id:
                print(f"  ERROR: current_user.id is None or invalid")
                with open('/tmp/otithi_debug.log', 'a') as f:
                    f.write(f"ERROR: current_user.id is None or invalid\\n")
                flash('Authentication error. Please log in again.', 'error')
                return render_template('host/create_listing.html')
            
            with open('/tmp/otithi_debug.log', 'a') as f:
                f.write(f"Attempting to create listing with:\\n")
                f.write(f"  host_id: {current_user.id}\\n")
                f.write(f"  location_id: {location_obj.location_id}\\n")
                f.write(f"  title: {title}\\n")
                f.write(f"  room_type: {room_type}\\n")
                f.write(f"  price: {price_per_night}\\n")
                f.write(f"  guests: {max_guests}\\n")
                
            listing = Listing.create(
                title=title,
                description=description,
                price=price_per_night,
                host_id=current_user.id,
                location_id=location_obj.location_id,
                property_type=room_type,
                guests=max_guests,
                amenities=amenities.split(',') if amenities else []
            )
            
            print(f"  Listing creation result: {listing}")
            with open('/tmp/otithi_debug.log', 'a') as f:
                f.write(f"Listing creation result: {listing}\\n")
                if listing:
                    f.write(f"SUCCESS: Listing created with ID {listing.id}\\n")
                else:
                    f.write(f"ERROR: Listing creation failed\\n")
            
            if listing:
                # Save images
                saved_images = []
                upload_dir = os.path.join('app', 'static', 'uploads', 'listings')
                os.makedirs(upload_dir, exist_ok=True)
                
                for file, order in uploaded_files:
                    try:
                        file_ext = file.filename.rsplit('.', 1)[1].lower()
                        unique_filename = f"listing_{listing.id}_{uuid.uuid4().hex[:8]}.{file_ext}"
                        
                        file_path = os.path.join(upload_dir, unique_filename)
                        file.save(file_path)
                        
                        image_record = ListingImage.create(
                            listing_id=listing.id,
                            image_filename=unique_filename,
                            image_order=order
                        )
                        
                        if image_record:
                            saved_images.append(unique_filename)
                        else:
                            try:
                                os.remove(file_path)
                            except:
                                pass
                    except Exception:
                        continue
                
                if saved_images:
                    flash(f'Listing "{title}" created successfully with {len(saved_images)} images!', 'success')
                else:
                    flash(f'Listing "{title}" created but no images were saved.', 'warning')
                
                return redirect(url_for('listings.listing_detail', listing_id=listing.id))
            else:
                flash('Failed to create listing. Please try again.', 'error')
        
        return render_template('host/create_listing.html')
    
    except Exception as e:
        flash('Error creating listing.', 'error')
        return render_template('host/create_listing.html')

# CRUD Operations for Listings

@listings_bp.route('/listings/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    """Edit an existing listing"""
    try:
        # Get the listing
        listing = Listing.get(listing_id)
        if not listing:
            flash('Listing not found.', 'error')
            return redirect(url_for('profile.my_listings'))
        
        # Check if current user owns this listing
        if listing.host_id != current_user.id:
            flash('You can only edit your own listings.', 'error')
            return redirect(url_for('profile.my_listings'))
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', '').strip()
            property_type = request.form.get('property_type', '').strip()
            guests = request.form.get('guests', '').strip()
            amenities = request.form.getlist('amenities')
            
            # Validate required fields
            if not all([title, description, price, property_type, guests]):
                flash('All fields are required.', 'error')
                return render_template('host/edit_listing.html', listing=listing)
            
            try:
                price = float(price)
                guests = int(guests)
            except ValueError:
                flash('Price must be a number and guests must be an integer.', 'error')
                return render_template('host/edit_listing.html', listing=listing)
            
            # Update the listing
            success = listing.update(
                title=title,
                description=description,
                price=price,
                property_type=property_type,
                guests=guests,
                amenities=amenities
            )
            
            if success:
                flash('Listing updated successfully!', 'success')
                return redirect(url_for('profile.my_listings'))
            else:
                flash('Failed to update listing. Please try again.', 'error')
        
        return render_template('host/edit_listing.html', listing=listing)
    
    except Exception as e:
        flash('Error updating listing.', 'error')
        return redirect(url_for('profile.my_listings'))

@listings_bp.route('/listings/<int:listing_id>/delete', methods=['POST'])
@login_required
def delete_listing(listing_id):
    """Delete a listing"""
    try:
        # Get the listing
        listing = Listing.get(listing_id)
        if not listing:
            flash('Listing not found.', 'error')
            return redirect(url_for('profile.my_listings'))
        
        # Check if current user owns this listing
        if listing.host_id != current_user.id:
            flash('You can only delete your own listings.', 'error')
            return redirect(url_for('profile.my_listings'))
        
        # Delete the listing
        success = listing.delete()
        
        if success:
            flash(f'Listing "{listing.title}" has been deleted successfully.', 'success')
        else:
            flash('Failed to delete listing. Please try again.', 'error')
    
    except Exception as e:
        flash('Error deleting listing.', 'error')
    
    return redirect(url_for('profile.my_listings'))

@listings_bp.route('/listings/<int:listing_id>/toggle-status', methods=['POST'])
@login_required
def toggle_listing_status(listing_id):
    """Toggle listing availability status"""
    try:
        # Get the listing
        listing = Listing.get(listing_id)
        if not listing:
            flash('Listing not found.', 'error')
            return redirect(url_for('profile.my_listings'))
        
        # Check if current user owns this listing
        if listing.host_id != current_user.id:
            flash('You can only modify your own listings.', 'error')
            return redirect(url_for('profile.my_listings'))
        
        # Toggle availability
        new_status = not listing.available
        query = "UPDATE listings SET available = %s WHERE listing_id = %s"
        success = db.execute_update(query, (new_status, listing_id))
        
        if success:
            status_text = "activated" if new_status else "deactivated"
            flash(f'Listing "{listing.title}" has been {status_text}.', 'success')
        else:
            flash('Failed to update listing status.', 'error')
    
    except Exception as e:
        flash('Error updating listing status.', 'error')
    
    return redirect(url_for('profile.my_listings'))
