"""add consulta estado

Revision ID: 2a9fb658a44b
Revises: 
Create Date: 2026-03-05 14:54:18.317196

"""
from alembic import op
import sqlalchemy as sa


revision = '2a9fb658a44b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if 'usuarios' not in tables:
        op.create_table(
            'usuarios',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nombre', sa.String(length=100), nullable=False),
            sa.Column('correo', sa.String(length=120), nullable=False),
            sa.Column('password', sa.String(length=255), nullable=False),
            sa.Column('tipo', sa.String(length=20), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('correo')
        )

    if 'duenos' not in tables:
        op.create_table(
            'duenos',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['id'], ['usuarios.id']),
            sa.PrimaryKeyConstraint('id')
        )

    if 'veterinarios' not in tables:
        op.create_table(
            'veterinarios',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['id'], ['usuarios.id']),
            sa.PrimaryKeyConstraint('id')
        )

    if 'mascotas' not in tables:
        op.create_table(
            'mascotas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nombre', sa.String(length=100), nullable=False),
            sa.Column('especie', sa.String(length=50), nullable=False),
            sa.Column('raza', sa.String(length=100), nullable=True),
            sa.Column('edad', sa.Integer(), nullable=False),
            sa.Column('fecha_registro', sa.DateTime(), nullable=True),
            sa.Column('dueno_id', sa.Integer(), nullable=False),
            sa.Column('imagen', sa.LargeBinary(), nullable=True),
            sa.Column('imagen_mimetype', sa.String(length=150), nullable=True),
            sa.ForeignKeyConstraint(['dueno_id'], ['usuarios.id']),
            sa.PrimaryKeyConstraint('id')
        )

    if 'consultas' not in tables:
        op.create_table(
            'consultas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('fecha', sa.DateTime(), nullable=True),
            sa.Column('motivo', sa.Text(), nullable=False),
            sa.Column('diagnostico', sa.Text(), nullable=True),
            sa.Column('tratamiento', sa.Text(), nullable=True),
            sa.Column('estado', sa.String(length=20), nullable=False, server_default='agendada'),
            sa.Column('mascota_id', sa.Integer(), nullable=False),
            sa.Column('veterinario_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['mascota_id'], ['mascotas.id']),
            sa.ForeignKeyConstraint(['veterinario_id'], ['usuarios.id']),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        columnas_consultas = {c['name'] for c in inspector.get_columns('consultas')}
        if 'estado' not in columnas_consultas:
            with op.batch_alter_table('consultas', schema=None) as batch_op:
                batch_op.add_column(
                    sa.Column('estado', sa.String(length=20), nullable=False, server_default='agendada')
                )

    if 'historial_medico' not in tables:
        op.create_table(
            'historial_medico',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('fecha', sa.DateTime(), nullable=True),
            sa.Column('descripcion', sa.Text(), nullable=False),
            sa.Column('diagnostico', sa.Text(), nullable=True),
            sa.Column('tratamiento', sa.Text(), nullable=True),
            sa.Column('mascota_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['mascota_id'], ['mascotas.id']),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if 'historial_medico' in tables:
        op.drop_table('historial_medico')
    if 'consultas' in tables:
        op.drop_table('consultas')
    if 'mascotas' in tables:
        op.drop_table('mascotas')
    if 'veterinarios' in tables:
        op.drop_table('veterinarios')
    if 'duenos' in tables:
        op.drop_table('duenos')
    if 'usuarios' in tables:
        op.drop_table('usuarios')
