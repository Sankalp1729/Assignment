#!/usr/bin/env python3
"""
Production Ready Application Entry Point

Optimized for deployment with proper error handling and logging
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for production deployment"""
    try:
        logger.info("="*70)
        logger.info("🚀 AI DDR GENERATOR — PRODUCTION MODE")
        logger.info("="*70)
        
        # Import here to ensure proper error handling
        from utils.observation_extractor import extract_observations
        from utils.merger import merge_observations, detect_conflicts
        from utils.severity import apply_severity_to_merged_data
        from utils.ddr_generator import generate_ddr_report, save_report, export_to_json
        import json
        
        # STEP 5: Extract observations
        logger.info("\n[1/8] EXTRACTING OBSERVATIONS...")
        try:
            observations = extract_observations()
            logger.info(f"✅ Extracted {len(observations)} observations")
        except Exception as e:
            logger.error(f"❌ Extraction failed: {str(e)}")
            return 1
        
        # STEP 6: Merge observations
        logger.info("\n[2/8] MERGING OBSERVATIONS...")
        try:
            merged, conflicts = merge_observations(observations)
            logger.info(f"✅ Merged observations, conflicts detected: {len(conflicts)}")
        except Exception as e:
            logger.error(f"❌ Merging failed: {str(e)}")
            return 1
        
        # STEP 7: Apply severity scoring
        logger.info("\n[3/8] SCORING SEVERITY...")
        try:
            severity_data = apply_severity_to_merged_data(merged)
            logger.info(f"✅ Severity scoring complete")
        except Exception as e:
            logger.error(f"❌ Severity scoring failed: {str(e)}")
            return 1
        
        # STEP 8: Generate report
        logger.info("\n[4/8] GENERATING REPORT...")
        try:
            report = generate_ddr_report(severity_data, conflicts, use_gemini=False)
            logger.info(f"✅ Report generated with {len(report)} sections")
        except Exception as e:
            logger.error(f"❌ Report generation failed: {str(e)}")
            return 1
        
        # Save outputs
        logger.info("\n[5/8] SAVING OUTPUTS...")
        try:
            save_report(report)
            export_to_json(report)
            logger.info("✅ Outputs saved")
        except Exception as e:
            logger.error(f"❌ Save failed: {str(e)}")
            return 1
        
        # Verify outputs
        logger.info("\n[6/8] VERIFYING OUTPUTS...")
        try:
            assert Path("outputs/ddr_report.txt").exists(), "Text report not generated"
            assert Path("outputs/ddr_report.json").exists(), "JSON report not generated"
            logger.info("✅ All outputs verified")
        except Exception as e:
            logger.error(f"❌ Verification failed: {str(e)}")
            return 1
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("✅ PRODUCTION RUN SUCCESSFUL")
        logger.info("="*70)
        logger.info("\n📊 RESULTS:")
        logger.info(f"  - Observations: {len(severity_data)}")
        logger.info(f"  - Conflicts: {len(conflicts)}")
        logger.info(f"  - Report sections: {len(report)}")
        logger.info(f"  - Output: outputs/ddr_report.txt")
        logger.info(f"           outputs/ddr_report.json")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ FATAL ERROR: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
