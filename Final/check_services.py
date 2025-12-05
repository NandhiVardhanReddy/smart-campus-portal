import os
import sys
import logging
from elasticsearch import Elasticsearch
import redis
from app.services.embedding_service import EmbeddingService
from app.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_embedding_service():
    logger.info("Checking EmbeddingService...")
    try:
        service = EmbeddingService()
        embedding = service.generate_embedding("test query")
        if embedding and len(embedding) == 384:
            logger.info("✅ EmbeddingService working correctly")
            return True
        else:
            logger.error("❌ EmbeddingService failed to generate valid embedding")
            return False
    except Exception as e:
        logger.error(f"❌ EmbeddingService error: {e}")
        return False

def check_elasticsearch():
    logger.info("Checking Elasticsearch...")
    try:
        es = Elasticsearch([Config.ELASTICSEARCH_URL], verify_certs=False)
        if es.ping():
            logger.info("✅ Elasticsearch connection successful")
            return True
        else:
            logger.error("❌ Could not connect to Elasticsearch")
            return False
    except Exception as e:
        logger.error(f"❌ Elasticsearch error: {e}")
        return False

def check_redis():
    logger.info("Checking Redis...")
    try:
        r = redis.from_url(Config.REDIS_URL)
        r.ping()
        logger.info("✅ Redis connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Redis error: {e}")
        return False

def main():
    logger.info("Starting service checks...")
    
    results = {
        "embedding": check_embedding_service(),
        "elasticsearch": check_elasticsearch(),
        "redis": check_redis()
    }
    
    if all(results.values()):
        logger.info("🎉 All services are running correctly!")
        sys.exit(0)
    else:
        logger.error("⚠️ Some services failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
