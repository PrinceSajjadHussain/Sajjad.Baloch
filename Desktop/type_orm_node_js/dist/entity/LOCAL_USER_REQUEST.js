"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.LOCAL_USER_REQUEST = void 0;
const typeorm_1 = require("typeorm");
const class_validator_1 = require("class-validator");
let LOCAL_USER_REQUEST = class LOCAL_USER_REQUEST {
    constructor() {
        this.ID = "";
        this.CREATED_BY_USER = '';
        this.CREATED_DATETIME = new Date();
        this.UPDATED_BY_USER = '';
        this.UPDATED_DATETIME = new Date();
        this.BOOL_SPARE1VAL = '0';
        this.BOOL_SPARE2VAL = '0';
        this.BOOL_SPARE3VAL = '0';
        this.BOOL_SPARE4VAL = '0';
        this.BOOL_SPARE5VAL = '0';
        this.CREATED_BY = '';
        this.DATE_CREATED = new Date();
        this.INT_SPARE1VAL = 0;
        this.INT_SPARE2VAL = 0;
        this.INT_SPARE3VAL = 0;
        this.INT_SPARE4VAL = 0;
        this.INT_SPARE5VAL = 0;
        this.IS_ENABLED = '1';
        this.LAST_UPDATED = new Date();
        this.MODIFIED_BY = '';
        this.STR_SPARE1VAL = '';
        this.STR_SPARE2VAL = '';
        this.STR_SPARE3VAL = '';
        this.STR_SPARE4VAL = '';
        this.STR_SPARE5VAL = '';
        this.BACK_END_MODULE = '';
        this.MODULE_STATUS = 0;
        this.STR_SPARE6VAL = '';
        this.STR_SPARE7VAL = '';
        this.DATE_SPARE1VAL = new Date();
        this.DATE_SPARE2VAL = new Date();
        this.DATE_SPARE3VAL = new Date();
        this.DATE_SPARE4VAL = new Date();
        this.DATE_SPARE5VAL = new Date();
        this.STR_SPARE8VAL = '';
        this.STR_SPARE9VAL = '';
        this.STR_SPARE10VAL = '';
        this.ROOM_ID = '';
        this.VIDEO_KYC_USER_ID = '';
        this.VIDEO_KYC_USER_NAME = '';
        this.OCR_COMPARISION = '0';
        this.ACCOUNT_OPENING_DATE = new Date();
        this.PBC_EMAIL = '';
        this.USER_REQUEST = '';
    }
};
exports.LOCAL_USER_REQUEST = LOCAL_USER_REQUEST;
__decorate([
    (0, typeorm_1.PrimaryColumn)({ type: 'varchar', length: 30 }),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 30),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "ID", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'CREATED_BY_USER', nullable: true, default: null, type: 'varchar2', length: 50 }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "CREATED_BY_USER", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'CREATED_DATETIME', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsDate)(),
    __metadata("design:type", Date)
], LOCAL_USER_REQUEST.prototype, "CREATED_DATETIME", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'UPDATED_BY_USER', nullable: true, default: null, type: 'varchar2', length: 50 }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "UPDATED_BY_USER", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'UPDATED_DATETIME', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsDate)(),
    __metadata("design:type", Date)
], LOCAL_USER_REQUEST.prototype, "UPDATED_DATETIME", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'BOOL_SPARE1VAL', type: 'char', length: 1, nullable: true, default: '0' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsIn)(['0', '1']),
    __metadata("design:type", Object)
], LOCAL_USER_REQUEST.prototype, "BOOL_SPARE1VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'BOOL_SPARE2VAL', type: 'char', length: 1, nullable: true, default: '0' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsIn)(['0', '1']),
    __metadata("design:type", Object)
], LOCAL_USER_REQUEST.prototype, "BOOL_SPARE2VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'BOOL_SPARE3VAL', type: 'char', length: 1, nullable: true, default: '0' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsIn)(['0', '1']),
    __metadata("design:type", Object)
], LOCAL_USER_REQUEST.prototype, "BOOL_SPARE3VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'BOOL_SPARE4VAL', type: 'char', length: 1, nullable: true, default: '0' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsIn)(['0', '1']),
    __metadata("design:type", Object)
], LOCAL_USER_REQUEST.prototype, "BOOL_SPARE4VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'BOOL_SPARE5VAL', type: 'char', length: 1, nullable: true, default: '0' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsIn)(['0', '1']),
    __metadata("design:type", Object)
], LOCAL_USER_REQUEST.prototype, "BOOL_SPARE5VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'CREATED_BY', nullable: true, default: null, type: 'varchar2', length: 50 }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "CREATED_BY", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'DATE_CREATED', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsDate)(),
    __metadata("design:type", Date)
], LOCAL_USER_REQUEST.prototype, "DATE_CREATED", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'INT_SPARE1VAL', nullable: false, default: null, type: 'number' }),
    (0, class_validator_1.IsNumber)(),
    __metadata("design:type", Number)
], LOCAL_USER_REQUEST.prototype, "INT_SPARE1VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'INT_SPARE2VAL', nullable: true, default: null, type: 'number' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsNumber)(),
    __metadata("design:type", Number)
], LOCAL_USER_REQUEST.prototype, "INT_SPARE2VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'INT_SPARE3VAL', nullable: true, default: null, type: 'number' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsNumber)(),
    __metadata("design:type", Number)
], LOCAL_USER_REQUEST.prototype, "INT_SPARE3VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'INT_SPARE4VAL', nullable: true, default: null, type: 'number' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsNumber)(),
    __metadata("design:type", Number)
], LOCAL_USER_REQUEST.prototype, "INT_SPARE4VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'INT_SPARE5VAL', nullable: true, default: null, type: 'number' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsNumber)(),
    __metadata("design:type", Number)
], LOCAL_USER_REQUEST.prototype, "INT_SPARE5VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'IS_ENABLED', type: 'char', length: 1, nullable: true, default: '1' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsIn)(['0', '1']),
    __metadata("design:type", Object)
], LOCAL_USER_REQUEST.prototype, "IS_ENABLED", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'LAST_UPDATED', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsDate)(),
    __metadata("design:type", Date)
], LOCAL_USER_REQUEST.prototype, "LAST_UPDATED", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'MODIFIED_BY', nullable: true, default: null, type: 'varchar2', length: 50 }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "MODIFIED_BY", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'STR_SPARE1VAL', length: 50, type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "STR_SPARE1VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'STR_SPARE2VAL', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "STR_SPARE2VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'STR_SPARE3VAL', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "STR_SPARE3VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'STR_SPARE4VAL', length: 50, type: 'varchar2' }),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "STR_SPARE4VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'STR_SPARE5VAL', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "STR_SPARE5VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'BACK_END_MODULE', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "BACK_END_MODULE", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'MODULE_STATUS', nullable: true, default: null, type: 'number' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsNumber)(),
    __metadata("design:type", Number)
], LOCAL_USER_REQUEST.prototype, "MODULE_STATUS", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'STR_SPARE6VAL', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "STR_SPARE6VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'STR_SPARE7VAL', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "STR_SPARE7VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'DATE_SPARE1VAL', type: 'date', nullable: true, default: null }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsDate)(),
    __metadata("design:type", Date)
], LOCAL_USER_REQUEST.prototype, "DATE_SPARE1VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'DATE_SPARE2VAL', type: 'date', nullable: true, default: null }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsDate)(),
    __metadata("design:type", Date)
], LOCAL_USER_REQUEST.prototype, "DATE_SPARE2VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'DATE_SPARE3VAL', type: 'date', nullable: true, default: null }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsDate)(),
    __metadata("design:type", Date)
], LOCAL_USER_REQUEST.prototype, "DATE_SPARE3VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'DATE_SPARE4VAL', type: 'date', nullable: true, default: null }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsDate)(),
    __metadata("design:type", Date)
], LOCAL_USER_REQUEST.prototype, "DATE_SPARE4VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'DATE_SPARE5VAL', type: 'date', nullable: true, default: null }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsDate)(),
    __metadata("design:type", Date)
], LOCAL_USER_REQUEST.prototype, "DATE_SPARE5VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'STR_SPARE8VAL', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "STR_SPARE8VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'STR_SPARE9VAL', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "STR_SPARE9VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'STR_SPARE10VAL', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "STR_SPARE10VAL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'ROOM_ID', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "ROOM_ID", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'VIDEO_KYC_USER_ID', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "VIDEO_KYC_USER_ID", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'VIDEO_KYC_USER_NAME', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "VIDEO_KYC_USER_NAME", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'OCR_COMPARISION', type: 'char', length: 1, nullable: true, default: '0' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsIn)(['0', '1']),
    __metadata("design:type", Object)
], LOCAL_USER_REQUEST.prototype, "OCR_COMPARISION", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'ACCOUNT_OPENING_DATE', type: 'date', nullable: true, default: null }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsDate)(),
    __metadata("design:type", Date)
], LOCAL_USER_REQUEST.prototype, "ACCOUNT_OPENING_DATE", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'PBC_EMAIL', length: 50, nullable: true, default: '', type: 'varchar2' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.Length)(0, 50),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "PBC_EMAIL", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'USER_REQUEST', type: 'clob', nullable: true, default: '' }),
    (0, class_validator_1.IsOptional)(),
    (0, class_validator_1.IsString)(),
    __metadata("design:type", String)
], LOCAL_USER_REQUEST.prototype, "USER_REQUEST", void 0);
exports.LOCAL_USER_REQUEST = LOCAL_USER_REQUEST = __decorate([
    (0, typeorm_1.Entity)({ name: 'BLINK_USER_REQUEST' }),
    __metadata("design:paramtypes", [])
], LOCAL_USER_REQUEST);