from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('cnpj', sa.String(length=14), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'unidades',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('cnes', sa.String(length=7), nullable=False),
        sa.Column('cnpj', sa.String(length=14), nullable=False),
        sa.Column('uf', sa.String(length=2), nullable=False),
        sa.Column('ibge_cod', sa.String(length=7), nullable=False),
        sa.Column('destino', sa.String(length=1), nullable=False),
        sa.Column('competencia_params', sa.JSON(), nullable=True),
    )
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('mfa_enabled', sa.Boolean(), default=False),
        sa.Column('ativo', sa.Boolean(), default=True),
    )
    op.create_table(
        'profissionais',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('unidade_id', sa.Integer(), sa.ForeignKey('unidades.id'), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('cpf', sa.String(length=11), nullable=False),
        sa.Column('cns', sa.String(length=15), nullable=False),
        sa.Column('cbo', sa.String(length=6), nullable=False),
        sa.Column('conselho', sa.String(length=50), nullable=True),
        sa.Column('certificado_publico', sa.Text(), nullable=True),
    )
    op.create_table(
        'pacientes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('cpf', sa.String(length=11), nullable=True),
        sa.Column('cns', sa.String(length=15), nullable=True),
        sa.Column('nome_social', sa.String(length=255), nullable=True),
        sa.Column('nome_mae', sa.String(length=255), nullable=True),
        sa.Column('sexo', sa.String(length=1), nullable=False),
        sa.Column('data_nascimento', sa.Date(), nullable=False),
        sa.Column('ibge_cod', sa.String(length=7), nullable=False),
        sa.Column('contato', sa.JSON(), nullable=True),
        sa.Column('pcd', sa.Boolean(), default=False),
        sa.Column('cid_deficiencia', sa.String(length=10), nullable=True),
    )
    op.create_table(
        'agendas',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('unidade_id', sa.Integer(), sa.ForeignKey('unidades.id'), nullable=False),
        sa.Column('profissional_id', sa.Integer(), sa.ForeignKey('profissionais.id'), nullable=False),
        sa.Column('paciente_id', sa.Integer(), sa.ForeignKey('pacientes.id'), nullable=True),
        sa.Column('data', sa.DateTime(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
    )
    op.create_table(
        'atendimentos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('unidade_id', sa.Integer(), sa.ForeignKey('unidades.id'), nullable=False),
        sa.Column('profissional_id', sa.Integer(), sa.ForeignKey('profissionais.id'), nullable=False),
        sa.Column('paciente_id', sa.Integer(), sa.ForeignKey('pacientes.id'), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('data', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
    )
    op.create_table(
        'evolucoes_prontuario',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('atendimento_id', sa.Integer(), sa.ForeignKey('atendimentos.id'), nullable=False),
        sa.Column('texto_estruturado', sa.Text(), nullable=False),
        sa.Column('hash_sha256', sa.String(length=64), nullable=False),
        sa.Column('assinado', sa.Boolean(), default=False),
        sa.Column('assinatura_meta', sa.JSON(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'anexos_clinicos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('atendimento_id', sa.Integer(), sa.ForeignKey('atendimentos.id'), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=False),
        sa.Column('hash', sa.String(length=64), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'procedimentos_sus',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('atendimento_id', sa.Integer(), sa.ForeignKey('atendimentos.id'), nullable=False),
        sa.Column('sigtap_codigo', sa.String(length=10), nullable=False),
        sa.Column('cid10', sa.String(length=10), nullable=False),
        sa.Column('quantidade', sa.Integer(), nullable=False),
        sa.Column('profissional_cbo', sa.String(length=6), nullable=False),
        sa.Column('valores', sa.JSON(), nullable=True),
        sa.Column('competencia_aaaamm', sa.String(length=6), nullable=False),
        sa.Column('validacoes_json', sa.JSON(), nullable=True),
    )
    op.create_table(
        'exportacoes_bpa',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('competencia', sa.String(length=6), nullable=False),
        sa.Column('unidade_id', sa.Integer(), sa.ForeignKey('unidades.id'), nullable=False),
        sa.Column('arquivo_path', sa.String(length=255), nullable=True),
        sa.Column('checksum', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('erros_json', sa.JSON(), nullable=True),
    )
    op.create_table(
        'exportacoes_apac',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('competencia', sa.String(length=6), nullable=False),
        sa.Column('unidade_id', sa.Integer(), sa.ForeignKey('unidades.id'), nullable=False),
        sa.Column('arquivo_path', sa.String(length=255), nullable=True),
        sa.Column('checksum', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('erros_json', sa.JSON(), nullable=True),
    )
    op.create_table(
        'competencias_abertas',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('unidade_cnes', sa.String(length=7), nullable=False),
        sa.Column('competencia', sa.String(length=6), nullable=False),
        sa.Column('aberta', sa.Boolean(), default=True),
        sa.Column('data_abertura', sa.Date(), nullable=True),
        sa.Column('data_fechamento_previsto', sa.Date(), nullable=True),
        sa.Column('dias_para_lancamento', sa.Integer(), nullable=True),
        sa.Column('cidade', sa.String(length=100), nullable=True),
        sa.Column('uf', sa.String(length=2), nullable=True),
    )
    op.create_table(
        'tabelas_sigtap',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('codigo', sa.String(length=10), nullable=False),
        sa.Column('descricao', sa.String(length=255), nullable=False),
        sa.Column('valor', sa.Numeric(10, 2), nullable=True),
        sa.Column('regras', sa.JSON(), nullable=True),
        sa.Column('vigencia', sa.String(length=6), nullable=False),
    )
    op.create_table(
        'tabelas_auxiliares',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('codigo', sa.String(length=20), nullable=False),
        sa.Column('descricao', sa.String(length=255), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
    )


def downgrade():
    op.drop_table('tabelas_auxiliares')
    op.drop_table('tabelas_sigtap')
    op.drop_table('competencias_abertas')
    op.drop_table('exportacoes_apac')
    op.drop_table('exportacoes_bpa')
    op.drop_table('procedimentos_sus')
    op.drop_table('anexos_clinicos')
    op.drop_table('evolucoes_prontuario')
    op.drop_table('atendimentos')
    op.drop_table('agendas')
    op.drop_table('pacientes')
    op.drop_table('profissionais')
    op.drop_table('usuarios')
    op.drop_table('unidades')
    op.drop_table('tenants')
