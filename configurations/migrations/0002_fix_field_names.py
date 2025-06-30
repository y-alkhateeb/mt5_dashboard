# Generated custom migration for field name fixes
# File: configurations/migrations/0002_fix_field_names.py

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('configurations', '0001_initial'),
    ]

    operations = [
        # First, handle the missing/renamed basic fields
        migrations.RunSQL(
            # Check if columns exist before renaming
            sql="""
            DO $$
            BEGIN
                -- Rename inp_AllowedSymbol to allowed_symbol if it exists
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'inp_AllowedSymbol') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_AllowedSymbol" TO allowed_symbol;
                END IF;
                
                -- Add allowed_symbol if it doesn't exist
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'configurations_tradingconfiguration' 
                              AND column_name = 'allowed_symbol') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN allowed_symbol VARCHAR(20) DEFAULT 'US30';
                END IF;
                
                -- Handle strict_symbol_check
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'inp_StrictSymbolCheck') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_StrictSymbolCheck" TO strict_symbol_check;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'strict_symbol_check') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN strict_symbol_check BOOLEAN DEFAULT true;
                END IF;
                
                -- Handle session_start
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'inp_SessionStart') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_SessionStart" TO session_start;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'session_start') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN session_start VARCHAR(5) DEFAULT '08:45';
                END IF;
                
                -- Handle session_end
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'inp_SessionEnd') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_SessionEnd" TO session_end;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'session_end') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN session_end VARCHAR(5) DEFAULT '10:00';
                END IF;
            END
            $$;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Handle Fibonacci fields mapping
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- Map fib_level_1_1 -> fib_primary_buy_tp
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'fib_level_1_1') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN fib_level_1_1 TO fib_primary_buy_tp;
                ELSIF EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name = 'configurations_tradingconfiguration' 
                             AND column_name = 'inp_FibLevel_1_1') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_FibLevel_1_1" TO fib_primary_buy_tp;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'fib_primary_buy_tp') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_primary_buy_tp NUMERIC(8,5) DEFAULT 1.325;
                END IF;
                
                -- Map fib_level_1_05 -> fib_primary_buy_entry
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'fib_level_1_05') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN fib_level_1_05 TO fib_primary_buy_entry;
                ELSIF EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name = 'configurations_tradingconfiguration' 
                             AND column_name = 'inp_FibLevel_1_05') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_FibLevel_1_05" TO fib_primary_buy_entry;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'fib_primary_buy_entry') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_primary_buy_entry NUMERIC(8,5) DEFAULT 1.05;
                END IF;
                
                -- Map fib_level_1_0 -> fib_session_high
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'fib_level_1_0') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN fib_level_1_0 TO fib_session_high;
                ELSIF EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name = 'configurations_tradingconfiguration' 
                             AND column_name = 'inp_FibLevel_1_0') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_FibLevel_1_0" TO fib_session_high;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'fib_session_high') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_session_high NUMERIC(8,5) DEFAULT 1.0;
                END IF;
                
                -- Map fib_level_0_0 -> fib_session_low
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'fib_level_0_0') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN fib_level_0_0 TO fib_session_low;
                ELSIF EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name = 'configurations_tradingconfiguration' 
                             AND column_name = 'inp_FibLevel_0_0') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_FibLevel_0_0" TO fib_session_low;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'fib_session_low') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_session_low NUMERIC(8,5) DEFAULT 0.0;
                END IF;
                
                -- Map fib_level_neg_05 -> fib_primary_sell_entry
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'fib_level_neg_05') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN fib_level_neg_05 TO fib_primary_sell_entry;
                ELSIF EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name = 'configurations_tradingconfiguration' 
                             AND column_name = 'inp_FibLevel_Neg_05') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_FibLevel_Neg_05" TO fib_primary_sell_entry;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'fib_primary_sell_entry') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_primary_sell_entry NUMERIC(8,5) DEFAULT -0.05;
                END IF;
                
                -- Map fib_level_neg_1 -> fib_primary_sell_tp
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'fib_level_neg_1') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN fib_level_neg_1 TO fib_primary_sell_tp;
                ELSIF EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name = 'configurations_tradingconfiguration' 
                             AND column_name = 'inp_FibLevel_Neg_1') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_FibLevel_Neg_1" TO fib_primary_sell_tp;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'fib_primary_sell_tp') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_primary_sell_tp NUMERIC(8,5) DEFAULT -0.325;
                END IF;
                
                -- Map fib_level_primary_buy_sl -> fib_primary_buy_sl
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'fib_level_primary_buy_sl') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN fib_level_primary_buy_sl TO fib_primary_buy_sl;
                ELSIF EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name = 'configurations_tradingconfiguration' 
                             AND column_name = 'inp_FibLevel_PrimaryBuySL') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_FibLevel_PrimaryBuySL" TO fib_primary_buy_sl;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'fib_primary_buy_sl') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_primary_buy_sl NUMERIC(8,5) DEFAULT -0.05;
                END IF;
                
                -- Map fib_level_primary_sell_sl -> fib_primary_sell_sl
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'fib_level_primary_sell_sl') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN fib_level_primary_sell_sl TO fib_primary_sell_sl;
                ELSIF EXISTS (SELECT 1 FROM information_schema.columns 
                             WHERE table_name = 'configurations_tradingconfiguration' 
                             AND column_name = 'inp_FibLevel_PrimarySellSL') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_FibLevel_PrimarySellSL" TO fib_primary_sell_sl;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'fib_primary_sell_sl') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_primary_sell_sl NUMERIC(8,5) DEFAULT 1.05;
                END IF;
                
                -- Continue with other hedge fields...
                -- Handle timeout fields
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'configurations_tradingconfiguration' 
                          AND column_name = 'inp_PrimaryPendingTimeout') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    RENAME COLUMN "inp_PrimaryPendingTimeout" TO primary_pending_timeout;
                ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                 WHERE table_name = 'configurations_tradingconfiguration' 
                                 AND column_name = 'primary_pending_timeout') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN primary_pending_timeout INTEGER DEFAULT 30;
                END IF;
                
                -- Add remaining timeout fields if missing
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'configurations_tradingconfiguration' 
                              AND column_name = 'primary_position_timeout') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN primary_position_timeout INTEGER DEFAULT 60;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'configurations_tradingconfiguration' 
                              AND column_name = 'hedging_pending_timeout') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN hedging_pending_timeout INTEGER DEFAULT 30;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'configurations_tradingconfiguration' 
                              AND column_name = 'hedging_position_timeout') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN hedging_position_timeout INTEGER DEFAULT 60;
                END IF;
                
                -- Add missing hedge fields
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'configurations_tradingconfiguration' 
                              AND column_name = 'fib_level_hedge_buy') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_level_hedge_buy NUMERIC(8,5) DEFAULT 1.05;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'configurations_tradingconfiguration' 
                              AND column_name = 'fib_level_hedge_sell') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_level_hedge_sell NUMERIC(8,5) DEFAULT -0.05;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'configurations_tradingconfiguration' 
                              AND column_name = 'fib_level_hedge_buy_sl') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_level_hedge_buy_sl NUMERIC(8,5) DEFAULT 0.0;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'configurations_tradingconfiguration' 
                              AND column_name = 'fib_level_hedge_sell_sl') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_level_hedge_sell_sl NUMERIC(8,5) DEFAULT 1.0;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'configurations_tradingconfiguration' 
                              AND column_name = 'fib_hedge_buy_tp') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_hedge_buy_tp NUMERIC(8,5) DEFAULT 1.3;
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'configurations_tradingconfiguration' 
                              AND column_name = 'fib_hedge_sell_tp') THEN
                    ALTER TABLE configurations_tradingconfiguration 
                    ADD COLUMN fib_hedge_sell_tp NUMERIC(8,5) DEFAULT -0.3;
                END IF;
            END
            $$;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]