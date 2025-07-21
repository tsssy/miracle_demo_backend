import sys
from pathlib import Path
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

ROOT_PATH = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_PATH))
from app.config import settings
from app.utils.my_logger import MyLogger

logger = MyLogger("database")


def convert_objectid_to_str(data):
    """将字典中的所有ObjectID转换为字符串"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, dict):
                convert_objectid_to_str(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_objectid_to_str(item)
    return data


class Database:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        """连接到 MongoDB"""
        try:
            # 使用同步客户端测试连接
            test_client = MongoClient(
                settings.MONGODB_URL,
                username=settings.MONGODB_USERNAME,
                password=settings.MONGODB_PASSWORD,
                authSource=settings.MONGODB_AUTH_SOURCE,
                serverSelectionTimeoutMS=5000,
            )
            test_client.server_info()  # 测试连接
            test_client.close()

            # 创建异步客户端
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                username=settings.MONGODB_USERNAME,
                password=settings.MONGODB_PASSWORD,
                authSource=settings.MONGODB_AUTH_SOURCE,
                serverSelectionTimeoutMS=5000,
            )
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close(cls):
        """关闭 MongoDB 连接"""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")

    @classmethod
    def get_db(cls):
        """获取数据库实例"""
        return cls.db

    @classmethod
    def get_collection(cls, collection_name: str):
        """获取集合实例"""
        return cls.get_db()[collection_name]

    @classmethod
    async def insert_one(cls, collection_name: str, document: dict):
        """插入单个文档"""
        try:
            result = await cls.get_collection(collection_name).insert_one(document)
            logger.info(f"Inserted document with id: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            raise

    @classmethod
    async def insert_many(cls, collection_name: str, documents: list):
        """插入多个文档"""
        try:
            result = await cls.get_collection(collection_name).insert_many(documents)
            logger.info(f"Inserted {len(result.inserted_ids)} documents")
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Error inserting documents: {e}")
            raise

    @classmethod
    async def find_one(cls, collection_name: str, query: dict):
        """查找单个文档"""
        try:
            result = await cls.get_collection(collection_name).find_one(query)
            return convert_objectid_to_str(result) if result else None
        except Exception as e:
            logger.error(f"Error finding document: {e}")
            raise

    @classmethod
    async def find(
        cls,
        collection_name: str,
        query: dict = {},
        projection: dict = {},
        limit: int = 0,
        sort: list = [],
    ):
        """查找多个文档"""
        try:
            cursor = cls.get_collection(collection_name).find(query, projection)
            if sort:
                cursor = cursor.sort(sort)
            if limit > 0:
                cursor = cursor.limit(limit)
            results = await cursor.to_list(length=None)
            return [convert_objectid_to_str(result) for result in results]
        except Exception as e:
            logger.error(f"Error finding documents: {e}")
            raise

    @classmethod
    async def update_one(cls, collection_name: str, query: dict, update: dict):
        """更新单个文档"""
        try:
            result = await cls.get_collection(collection_name).update_one(query, update)
            # logger.info(f"Modified {result.modified_count} document")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise

    @classmethod
    async def update_many(cls, collection_name: str, query: dict, update: dict):
        """更新多个文档"""
        try:
            result = await cls.get_collection(collection_name).update_many(
                query, update
            )
            # logger.info(f"Modified {result.modified_count} documents")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            raise

    @classmethod
    async def delete_one(cls, collection_name: str, query: dict):
        """删除单个文档"""
        try:
            result = await cls.get_collection(collection_name).delete_one(query)
            logger.info(f"Deleted {result.deleted_count} document")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

    @classmethod
    async def delete_many(cls, collection_name: str, query: dict):
        """删除多个文档"""
        try:
            result = await cls.get_collection(collection_name).delete_many(query)
            logger.info(f"Deleted {result.deleted_count} documents")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise


if __name__ == "__main__":
    # 测试数据库连接
    import asyncio

    async def main():
        # 由于是 classmethod，直接通过类调用 connect
        await Database.connect()
        print("Database connected successfully in test.")

        # 简单的插入和查找测试
        test_document = {"test_key": "test_value", "timestamp": datetime.utcnow()}
        inserted_id = await Database.insert_one("test_collection", test_document)
        print(f"Inserted document with ID: {inserted_id}")

        found_doc = await Database.find_one("test_collection", {"_id": ObjectId(inserted_id)})
        print(f"Found document: {found_doc}")

        # 确保在测试结束时关闭连接
        await Database.close()

    # 运行测试
    if __name__ == "__main__":
        from datetime import datetime
        # 导入 config 以确保 settings 可用
        from app.config import settings
        asyncio.run(main()) 