from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic
revision = 'acdb1d9dbad2'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # First add the 'email' column with nullable=True
    op.add_column('user', sa.Column('email', sa.String(length=120), nullable=True))
    
    # Optionally: You can update the existing records to fill in the email column (if necessary)
    # For example, update all users with a default email for the migration:
    op.execute("UPDATE user SET email = 'default@example.com' WHERE email IS NULL")
    
    # Then alter the column to set nullable=False (this is safe now since it has values)
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('email', nullable=False)
    
    # Add unique constraint to the email column
    with op.batch_alter_table('user') as batch_op:
        batch_op.create_unique_constraint('uq_email', ['email'])

def downgrade():
    # Drop the unique constraint
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_constraint('uq_email', type_='unique')
    
    # Drop the 'email' column
    op.drop_column('user', 'email')
