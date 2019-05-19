# Generated by Django 2.2.1 on 2019-05-19 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('providers', '0016_externaltransaction_is_imported'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externalaccount',
            name='associated',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_account_link', to='portfolio.Account'),
        ),
        migrations.AlterField(
            model_name='externalaccount',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_account_currency_rel', to='common.Currency'),
        ),
        migrations.AlterField(
            model_name='externalaccount',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_account_providing_company', to='common.Company'),
        ),
        migrations.AlterField(
            model_name='externalaccount',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_account_type_rel', to='portfolio.AccountType'),
        ),
        migrations.AlterField(
            model_name='externalportfolioholdings',
            name='portfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='portfolio_holdings_portfolio', to='portfolio.Portfolio'),
        ),
        migrations.AlterField(
            model_name='externalportfolioholdings',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='portfolio_holdings_provider', to='common.Company'),
        ),
        migrations.AlterField(
            model_name='externalsecurity',
            name='associated',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_security_link', to='security.Security'),
        ),
        migrations.AlterField(
            model_name='externalsecurity',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_security_currency_rel', to='common.Currency'),
        ),
        migrations.AlterField(
            model_name='externalsecurity',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_security_providing_company', to='common.Company'),
        ),
        migrations.AlterField(
            model_name='externalsecurity',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_security_type_rel', to='security.SecurityType'),
        ),
        migrations.AlterField(
            model_name='externaltransaction',
            name='external_security',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_transaction_security', to='providers.ExternalSecurity'),
        ),
        migrations.AlterField(
            model_name='externaltransaction',
            name='external_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_transaction_source', to='providers.ExternalAccount'),
        ),
        migrations.AlterField(
            model_name='externaltransaction',
            name='external_target',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_transaction_target', to='providers.ExternalAccount'),
        ),
        migrations.AlterField(
            model_name='externaltransaction',
            name='internal_operation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_transaction_operation', to='portfolio.Operation'),
        ),
        migrations.AlterField(
            model_name='externaltransaction',
            name='portfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_transaction_portfolio', to='portfolio.Portfolio'),
        ),
        migrations.AlterField(
            model_name='externaltransaction',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_transaction_provider', to='common.Company'),
        ),
        migrations.AlterField(
            model_name='portfolioaccountholding',
            name='external_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_account_holding', to='providers.ExternalAccount'),
        ),
        migrations.AlterField(
            model_name='portfolioaccountholding',
            name='internal_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='internal_account_holding', to='portfolio.Account'),
        ),
        migrations.AlterField(
            model_name='portfoliosecurityholding',
            name='external_security',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='external_security_holding', to='providers.ExternalSecurity'),
        ),
        migrations.AlterField(
            model_name='portfoliosecurityholding',
            name='internal_security',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='internal_security_holding', to='security.Security'),
        ),
    ]
